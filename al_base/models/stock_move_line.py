from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    supplier_lot = fields.Char('Lote Proveedor')

    @api.onchange('product_id')
    def on_change_product_id(self):
        for item in self:
            res = {
                'attrs': {
                    'supplier_lot': {'readonly': [('product_id.tracking', '=', 'lot')]}}
            }
            return res
