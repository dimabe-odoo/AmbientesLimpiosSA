from odoo import models, fields, api
from py_linq import Enumerable


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    supplier_lot = fields.Char('Lote Proveedor')

    is_prd_lot = fields.Boolean('Es lote produccido')

    location_id = fields.Many2one('stock.location', compute='compute_location_id')

    @api.model
    def create(self, values):
        lot = self.env['stock.production.lot'].search(
            [('name', '=', values['name']), ('product_id', '=', values['product_id'])])
        if lot:
            return
        res = super(StockProductionLot, self).create(values)
        return res

    def compute_location_id(self):
        for item in self:
            location_id = Enumerable(item.quant_ids).select(
                lambda x: x.location_id.usage == 'internal' and x.quantity > 0)
            item.location_id = location_id
