from odoo import fields, models, api


class ProductLine(models.Model):
    _name = 'product.line'

    product_id = fields.Many2one('product.product',string='Producto')

    qty_to_delivery = fields.Float('Cantidad a Entregar')

    line_id = fields.Many2one('route.map.line',string='Linea de Ruta')