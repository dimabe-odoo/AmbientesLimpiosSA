from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'purchase.order'

    date_delivered = fields.Date(string='Fecha de Entrega')