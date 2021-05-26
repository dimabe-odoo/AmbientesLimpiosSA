from odoo import fields, models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.constrains("product_id","quantity")
    def check_negative_qty(self):
        if 'Subcontract' in self.location_id.name:
            return
        return super(StockQuant, self).check_negative_qty()