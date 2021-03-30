from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    supplier_lot = fields.Char('Lote Proveedor')