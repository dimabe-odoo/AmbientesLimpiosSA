from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    file_pdf = fields.Binary(string='OC')

    is_comercionet = fields.Boolean('Es de comercionet',default=False)

    comercionet_id = fields.Many2one('sale.order.comercionet')

    comercionet_pdf = fields.Binary(string='OC',related='comercionet_id.pdf_file')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_list_comercionet = fields.Integer('Precio Lista Comercionet')