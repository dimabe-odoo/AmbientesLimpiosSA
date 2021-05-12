import json

from odoo import models, fields, api
from ..utils import comercionet_scrapper
from ..utils import download_pdf
from ..utils import edi_comercionet
from datetime import datetime
from py_linq import Enumerable
import requests


class SaleOrderComercionet(models.Model):
    _name = 'sale.order.comercionet'
    _rec_name = 'purchase_order'
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
    have_client = fields.Boolean('Tiene Cliente',compute='compute_have_client')
    have_sale_order = fields.Boolean('Tiene Nota de Venta',compute='compute_have_sale_order')
    line_without_product = fields.Boolean('Tiene Una linea sin producto',compute='compute_line_without_product')
    have_pdf = fields.Boolean('Tiene PDF',compute='compute_have_pdf')

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
        product = self.env['product.product'].search([('al_dun', '=', product_code)], limit=1)
        if not product:
            p_tmpl = self.env['product.template'].search([('al_dun', '=', product_code)], limit=1)
            if p_tmpl:
                product = self.env['product.product'].search([('product_tmpl_id', '=', p_tmpl.id)])
                if product:
                    product.write({
                        'al_dun': p_tmpl.al_dun,
                        'al_sku': p_tmpl.al_sku
                    })
            else:
                product = self.env['product.product'].search([('barcode', '=', product_code)], limit=1)
                if not product:
                    product = self.env['product.template'].search([('barcode', '=', product_code)], limit=1)
        return product

    def update_product_id_line(self):
        for line in self.comercionet_line_id:
            if not line.product_id:
                product = self.get_product(line.product_code)
                line.write({
                    'product_id': product.id
                })

    def create_sale_order(self):
        if not self.client_id:
            raise models.ValidationError('El cliente no se encuentra establecido')
        if self.client_id and self.client_code_comercionet:
            for line in self.comercionet_line_id:
                if not line.product_id:
                    raise models.ValidationError('la linea {} no cuenta con un producto asociado'.format(line.number))
        sale_order = self.env['sale.order'].create({
            'date_order': datetime.now(),
            'l10n_latam_document_type_id': self.env['l10n_latam.document.type'].search([('code','=',33)]).id,
            'partner_id': self.client_id.parent_id.id if self.client_id.parent_id else self.client_id.id,
            'partner_shipping_id': self.client_id.id,
            'state': 'toconfirm',
            'picking_policy': 'direct',
            'pricelist_id': self.client_id.property_product_pricelist.id,
            'user_id': self.client_id.user_id.id if self.client_id.user_id else None,
            'warehouse_id': self.env['stock.warehouse'].search([('code','=','BoD01')]).id,
        })
        for line in self.comercionet_line_id:
            self.env['sale.order.line'].create({
                'product_id': line.product_id.id,
                'customer_lead': 3,
                'name': line.product_id.display_name,
                'order_id': sale_order.id,
                'price_unit': line.price,
                'product_uom_qty': line.quantity,
                'price_subtotal': line.final_price,
                'discount': line.discount_percent if line.discount_percent > 0 else 0
            })
        self.write({
            'sale_order_id': sale_order.id
        })

    def update_secondary_box(self):
        if not self.secondary_comercionet_box and self.doc:
            sale_order = edi_comercionet.create_sale_order_by_edi(self.doc)
            self.write({
                'secondary_comercionet_box': sale_order['secondary_comercionet_box']
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
        print("Hola")
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
                            'quantity': line['quantity'],
                            'discount_percent': line['discount_percent'],
                            'comercionet_id': comercionet.id,
                            'product_id': product.id if product else None
                        })


    class SaleOrderComercionetLine(models.Model):
        _name = 'sale.order.comercionet.line'
        number = fields.Integer('Linea de Pedido')
        product_code = fields.Char('Código Producto (DUN)')
        final_price = fields.Integer('Precio Final')
        price = fields.Integer('Precio Unitario')
        quantity = fields.Integer('Cantidad')
        discount_percent = fields.Float('Descuento')
        comercionet_id = fields.Many2one('sale.order.comercionet')
        product_id = fields.Many2one('product.product', string='Producto')
