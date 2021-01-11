from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    al_sku = fields.Char(string='Código Sysgestion')
    al_dun = fields.Char(string='DUN')