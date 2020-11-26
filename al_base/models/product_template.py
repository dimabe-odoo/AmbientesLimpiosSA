from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    al_sku = fields.Char(string='SKU')
    al_dun = fields.Char(string='DUN')