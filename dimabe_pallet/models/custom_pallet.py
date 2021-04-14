from odoo import fields, models


class CustomPallet(models.Model):
    _name = 'custom.pallet'

    name = fields.Char('Nombre')

    lot_id = fields.Many2one('stock.production.lot', string='Lote')

    product_ids = fields.Many2many('product.product')