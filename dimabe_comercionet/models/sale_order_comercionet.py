from odoo import models, fields
from ..utils import comercionet_scrapper
from ..utils import download_pdf

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

    def _compute_total(self):
        for item in self:
            item.total_price = sum(item.comercionet_line_id.mapped('final_price'))

    def download_pdfs(self):
        search = self.env['sale.order.comercionet'].search([('pdf_file', '=', None)])
        if search:
            documents = []
            for doc in search:
                documents.append(doc.doc_id)
            if len(documents) > 0:
                res = download_pdf.download_pdfs(documents)
                if res and len(res) > 0:
                    for d in res:
                        so = self.env['sale.order.comercionet'].search([('doc_id', '=', d['doc_id'])], limit=1)
                        if so:
                            so.write(
                                {'pdf_file' : d['pdf_file']}
                            )

    def get_orders(self):
        orders = comercionet_scrapper.get_sale_orders()
        if orders:
            for order in orders:
                sale = self.env['sale.order.comercionet'].search([('purchase_order', '=', order['purchase_order'].strip())])
                if not sale:
                    client_code = order['client_code_comercionet'].strip()
                    secondary_client_code = order['secondary_comercionet_box'].strip()
                    client = self.env['res.partner'].search([('comercionet_box', 'like', f'%{client_code}%')], limit=1)
                    if not client:
                        self.env['res.partner'].search([('comercionet_box', 'like', f'%{secondary_client_code}%')], limit=1)
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
