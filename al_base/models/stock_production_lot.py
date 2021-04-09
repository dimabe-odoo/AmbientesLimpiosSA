from odoo import models, fields

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    supplier_lot = fields.Char('Lote Proveedor')
