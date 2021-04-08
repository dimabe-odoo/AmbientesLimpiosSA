from odoo import models, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    supplier_lot = fields.Char('Lote Proveedor')

    is_loteable = fields.Boolean(compute='_compute_is_loteable')

    def _compute_is_loteable(self):
        return self.product_id.tracking == 'lot'

