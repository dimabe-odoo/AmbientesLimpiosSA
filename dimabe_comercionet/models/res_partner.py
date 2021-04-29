from odoo import models, fields
class ResPartner(models.Model):
    _inherit = 'res.partner'

    comercionet_box = fields.Char('Casilla Comercionet')