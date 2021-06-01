from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    file_pdf = fields.Binary(string='Pdf')

    comercionet_id = fields.Many2one('sale.order.comercionet')

    comercionet_pdf = fields.Binary(string='PDF Comercionet',releated='comercionet_id.pdf_file')