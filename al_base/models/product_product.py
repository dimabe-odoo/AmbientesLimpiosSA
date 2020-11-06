from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    al_sku = fields.Char(string='SKU')
    al_dun = fields.Char(string='DUN')
