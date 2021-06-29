import json

from odoo import models, fields, api
from ..utils import comercionet_scrapper
from ..utils import download_pdf
from ..utils import edi_comercionet
from datetime import datetime
from py_linq import Enumerable
import pytz
import requests
from ..utils.util import get_price_list


class SaleOrderComercionet(models.Model):
    _name = 'sale.order.comercionet'
    _rec_name = 'purchase_order'
    _order = 'create_date desc'
    purchase_order = fields.Char('Orden de compra')
    client_code_comercionet = fields.Char('Casilla Comercionet')
    secondary_comercionet_box = fields.Char('Segunda Casilla Comercionet')
    client_id = fields.Many2one('res.partner', string='Cliente')
    sale_order_id = fields.Many2one('sale.order', string='Nota de Venta')
    comercionet_line_id = fields.One2many('sale.order.comercionet.line', 'comercionet_id')
    total_price = fields.Float('Total', compute='_compute_total')
    doc_id = fields.Char('Id Documento Comercionet')
    doc = fields.Char('Documento EDI')
    pdf_file = fields.Binary('OC PDF')
    comercionet_create_date = fields.Date('Fecha OC')
    comercionet_dispatched_date = fields.Date('Fecha Entrega')
    have_client = fields.Boolean('Tiene Cliente', compute='compute_have_client')
    have_sale_order = fields.Boolean('Tiene Nota de Venta', compute='compute_have_sale_order')
    have_dates = fields.Boolean('Tiene Fechas', compute='compute_have_dates')
    line_without_product = fields.Boolean('Tiene Una linea sin producto', compute='compute_line_without_product')
    have_pdf = fields.Boolean('Tiene PDF', compute='compute_have_pdf')

    def compute_have_dates(self):
        show = True
        if not self.comercionet_create_date and self.comercionet_dispatched_date:
            show = False
        self.have_dates = show

    def compute_have_pdf(self):
        show = True
        if not self.pdf_file:
            show = False
        self.have_pdf = show

    def compute_have_client(self):
        show = True
        if not self.client_id:
            show = False
        self.have_client = show

    def compute_have_sale_order(self):
        show = True
        if not self.sale_order_id:
            show = False
        self.have_sale_order = show

    def compute_line_without_product(self):
        show = True
        lines = Enumerable(self.comercionet_line_id)
        if lines.any(lambda x: not x.product_id):
            show = False
        self.line_without_product = show

    def _compute_total(self):
        for item in self:
            item.total_price = sum(item.comercionet_line_id.mapped('final_price'))

    def write(self, values):
        res = super(SaleOrderComercionet, self).write(values)

        if self.client_id:
            if not self.client_id.comercionet_box:
                box = self.secondary_comercionet_box if self.secondary_comercionet_box else self.client_code_comercionet
                c_box = self.env['res.partner'].search([('comercionet_box', 'like', f'%{box}%')])
                if c_box:
                    raise models.ValidationError(f'La casilla {box} se encuentra asociada a {c_box.name}')
                self.client_id.write({
                    'comercionet_box': box
                })
        return res

    def get_product(self, product_code):
        product_code = product_code.lstrip('0')
        product = self.env['product.product'].search([('al_dun', '=', product_code)], limit=1, order='id desc')
        if not product:
            p_tmpl = self.env['product.template'].search([('al_dun', '=', product_code)], limit=1, order='id desc')
            if p_tmpl:
                product = self.env['product.product'].search([('product_tmpl_id', '=', p_tmpl.id)], limit=1,
                                                             order='id desc')
                if product:
                    product.write({
                        'al_dun': p_tmpl.al_dun,
                        'al_sku': p_tmpl.al_sku
                    })
            else:
                product = self.env['product.product'].search([('barcode', '=', product_code)], limit=1, order='id desc')
                if not product:
                    product = self.env['product.template'].search([('barcode', '=', product_code)], limit=1,
                                                                  order='id desc')
        return product

    def update_product_id_line(self):
        for line in self.comercionet_line_id:
            if not line.product_id:
                product = self.get_product(line.product_code)
                line.write({
                    'product_id': product.id
                })

    def create_sale_order(self):
        fields.Datetime.to_string(
            pytz.timezone(self.env.context['tz']).localize(fields.Datetime.from_string(datetime.datetime.now()),
                                                           is_dst=None).astimezone(pytz.utc))
        if not self.client_id:
            raise models.ValidationError('El cliente no se encuentra establecido')
        # if self.client_id and self.client_code_comercionet:--
        #    for line in self.comercionet_line_id:
        #        if not line.product_id:
        #            raise models.ValidationError('la linea {} no cuenta con un producto asociado'.format(line.number))
        sale_order = self.env['sale.order'].create({
            'date_order': fields.Datetime.to_string(
            pytz.timezone(self.env.context['tz']).localize(fields.Datetime.from_string(datetime.now()),
                                                           is_dst=None).astimezone(pytz.utc)),
            'l10n_latam_document_type_id': self.env['l10n_latam.document.type'].search([('code', '=', 33)]).id,
            'partner_id': self.client_id.parent_id.id if self.client_id.parent_id else self.client_id.id,
            'partner_shipping_id': self.client_id.id,
            'state': 'toconfirm',
            'picking_policy': 'direct',
            'payment_term_id': self.client_id.parent_id.property_payment_term_id.id,
            'pricelist_id': self.client_id.property_product_pricelist.id,
            'client_order_ref': self.purchase_order,
            'validity_date': fields.Datetime.to_string(
            pytz.timezone(self.env.context['tz']).localize(fields.Datetime.from_string(self.comercionet_dispatched_date),
                                                           is_dst=None).astimezone(pytz.utc)),
            'user_id': self.client_id.user_id.id if self.client_id.user_id else None,
            'warehouse_id': self.env['stock.warehouse'].search([('code', '=', 'BoD01')]).id,
            'comercionet_id': self.id,
            'is_comercionet': True
        })

        line_ids = []
        for line in self.comercionet_line_id:
            if line.product_id:
                line_ids.append({
                    'product_id': line.product_id.id,
                    'customer_lead': 3,
                    'name': line.product_id.display_name,
                    'order_id': sale_order.id,
                    'price_unit': line.price,
                    'price_list_comercionet': line.price_list,
                    'product_uom_qty': line.quantity,
                    'price_subtotal': line.final_price,
                    'discount': line.discount_percent if line.discount_percent > 0 else 0
                })
        self.env['sale.order.line'].create(line_ids)

        self.write({
            'sale_order_id': sale_order.id
        })

    def update_secondary_box(self):
        if not self.secondary_comercionet_box and self.doc:
            sale_order = edi_comercionet.create_sale_order_by_edi(self.doc)
            print(sale_order)
            self.write({
                'secondary_comercionet_box': sale_order['secondary_comercionet_box']
            })

    def update_date(self):
        if not self.comercionet_dispatched_date or not self.comercionet_create_date and self.doc:
            sale_order = edi_comercionet.create_sale_order_by_edi(self.doc)
            self.write({
                'comercionet_create_date': sale_order['create_date'],
                'comercionet_dispatched_date': sale_order['dispatch_date'],
            })

    def update_price_list(self):
        for line in self.comercionet_line_id:
            line.write({
                'price_list': get_price_list(line.product_id, self.client_id)
            })

    def download_oc_pdf(self):
        attachment = self.env['ir.attachment'].sudo().create({
            'name': f"OC {self.purchase_order}.pdf",
            'datas': self.pdf_file
        })
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment.id, ),
            'target': 'self',
        }
        return action

    def download_pdfs(self):
        search = self.env['sale.order.comercionet'].search([('pdf_file', '=', None)])
        if search:
            documents = []
            for doc in search:
                documents.append(doc.doc_id)
            if len(documents) > 0:
                url = self.env['ir.config_parameter'].search([('key', '=', 'pdf_url')]).value
                user = self.env['ir.config_parameter'].search([('key', '=', 'pdf_user')])
                password = self.env['ir.config_parameter'].search([('key', '=', 'pdf_password')])
                documents_json = {'documents': documents, "user": user.value, "password": password.password}
                res = requests.post(url, json=documents_json)
                result = res.json()
                if res.status_code == 200:
                    for d in result['result']:
                        so = self.env['sale.order.comercionet'].search([('doc_id', '=', d['doc_id'])], limit=1)
                        if so:
                            so.write(
                                {'pdf_file': d['pdf_file']}
                            )

    def assign_client(self):
        client = self.env['res.partner'].search([('comercionet_box', 'like', f'%{self.client_code_comercionet}%')],
                                                limit=1)
        if not client:
            client = self.env['res.partner'].search(
                [('comercionet_box', 'like', f'%{self.secondary_comercionet_box}%')],
                limit=1)
        if client:
            self.write({
                'client_id': client.id
            })

    def get_orders(self):
        orders = comercionet_scrapper.get_sale_orders()
        if orders:
            for order in orders:
                sale = self.env['sale.order.comercionet'].search(
                    [('purchase_order', '=', order['purchase_order'].strip())])
                if not sale:
                    if 'client_code_comercionet' not in order.keys():
                        order['client_code_comercionet'] = order['secondary_comercionet_box']
                    client_code = order['client_code_comercionet'].strip()
                    secondary_client_code = order['secondary_comercionet_box'].strip()
                    client = self.env['res.partner'].search([('comercionet_box', 'like', f'%{client_code}%')], limit=1)
                    if not client:
                        client = self.env['res.partner'].search(
                            [('comercionet_box', 'like', f'%{secondary_client_code}%')],
                            limit=1)
                    comercionet = self.env['sale.order.comercionet'].create({
                        'purchase_order': order['purchase_order'].strip(),
                        'client_code_comercionet': client_code,
                        'secondary_comercionet_box': secondary_client_code,
                        'doc_id': order['doc_id'],
                        'doc': order['doc'],
                        'comercionet_create_date': order['create_date'],
                        'comercionet_dispatched_date': order['dispatch_date'],
                        'client_id': client.id if client else None
                    })
                    for line in order['lines']:
                        product_code = line['product_code'].strip()
                        product = self.get_product(product_code)
                        self.env['sale.order.comercionet.line'].create({
                            'number': line['number'],
                            'product_code': product_code,
                            'final_price': line['final_price'],
                            'price': line['price'],
                            'price_list': get_price_list(product, client),
                            'quantity': line['quantity'],
                            'discount_percent': line['discount_percent'],
                            'comercionet_id': comercionet.id,
                            'product_id': product.id if product else None
                        })

    def can_edit(self, field):
        if self.have_sale_order:
            return False
        elif field in ['product_id', 'final_price', 'price']:
            return True
        else:
            return False


class SaleOrderComercionetLine(models.Model):
    _name = 'sale.order.comercionet.line'
    number = fields.Integer('Linea de Pedido')
    product_code = fields.Char('Código Producto (DUN)')
    final_price = fields.Integer('Precio Final')
    price = fields.Integer('Precio Comercionet')
    price_list = fields.Integer('Precio Lista', default=0)
    quantity = fields.Integer('Cantidad')
    discount_percent = fields.Float('Descuento')
    comercionet_id = fields.Many2one('sale.order.comercionet')
    product_id = fields.Many2one('product.product', string='Producto')
    price_difference = fields.Integer('Diferencia', compute="_compute_price_difference")
    have_sale_order = fields.Boolean(compute="_compute_have_sale_order")

    def _compute_price_difference(self):
        for item in self:
            if item.price:
                item.price_difference = abs(item.price - item.price_list)
            else:
                item.price_difference = 0

    def _compute_have_sale_order(self):
        for item in self:
            item.have_sale_order = self.comercionet_id.have_sale_order

    def write(self, values):
        if 'product_id' in values.keys():
            if self.comercionet_id.client_id:
                new_product_id = self.env['product.product'].search([('id', '=', values['product_id'])])
                price_list = get_price_list(new_product_id, self.comercionet_id.client_id)
                if price_list:
                    values['product_code'] = new_product_id.al_dun
                    values['price_list'] = price_list
                else:
                    client = self.comercionet_id.client_id.name
                    if self.comercionet_id.client_id.parent_id:
                        client = self.comercionet_id.client_id.parent_id.name
                    raise models.ValidationError(
                        f'El producto seleccionado: {new_product_id.name}  \nNo posee precio lista para cliente {client} \nFavor registrar')

            else:
                raise models.ValidationError(
                    'Para editar el producto, La orden de Venta Comercionet debe tener un Cliente asignado para obtener el precio de lista del producto')

        edit_price = False

        new_price = self.price
        new_final_price = self.final_price
        if 'price' in values.keys():
            new_price = values['price']
            if values['price'] != self.price:
                edit_price = True
        if 'final_price' in values.keys():
            new_final_price = values['final_price']
            if values['final_price'] != self.final_price:
                edit_price = True

        if edit_price:
            if new_price * self.quantity < new_final_price:
                raise models.ValidationError(
                    f'Precio Comercionet {new_price} x {self.quantity}  no puede ser menor al precio final {new_final_price}')
            else:
                discount_percent = 100 - ((new_final_price / (new_price * self.quantity)) * 100)
                values['discount_percent'] = discount_percent

        return super(SaleOrderComercionetLine, self).write(values)
