from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    al_sku = fields.Char(string='Código Sysgestion')
    al_dun = fields.Char(string='DUN')
    allow_consume_zero_in_op = fields.Boolean(default=False, string="Permitir consumo cero en OP", help="Permitir consumo en 0 en Órden de Producción")
