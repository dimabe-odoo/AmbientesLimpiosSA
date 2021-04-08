from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    supplier_lot = fields.Char('Lote Proveedor')

    @api.onchange('product_id')
    def on_change_product_id(self):
        for item in self:
            if item.product_id.tracking == 'lot':
                res = {
                    'readonly': {
                        'supplier_lot': 0
                    }
                }
            else:
                res = {
                    'readonly': {
                        'supplier_lot' : 1
                    }
                }
            return res
