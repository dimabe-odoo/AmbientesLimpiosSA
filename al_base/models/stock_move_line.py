from odoo import models, fields
from datetime import date


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    supplier_lot = fields.Char('Lote Proveedor')