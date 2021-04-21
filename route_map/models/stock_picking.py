from odoo import fields, models, api


class StockPickings(models.Model):
    _inherit = 'stock.picking'

    is_delivered = fields.Boolean()

    map_id = fields.Many2one('route.map', string='Hoja de Ruta')



