from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    pdf_file = fields.Binary(string='OC',compute='compute_pdf')

    def compute_pdf(self):
        for item in self:
            if item.sale_id:
                item.pdf_file = item.sale_id.comercionet_pdf if item.sale_id.is_comercionet else item.sale_id.file_pdf
