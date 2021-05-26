from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    certificate_logo = fields.Binary(string='Logo certificado')

    copies_qty = fields.Integer(string="Cantidad de copias cedibles")