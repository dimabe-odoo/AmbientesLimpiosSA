from odoo import fields, models, api

class CustomRangeApprovePurchase(models.Model):
    _name = 'custom.range.approve.purchase'

    name = fields.Char('Nombre')
    user_ids = fields.Many2many('res.users', string='Usuarios')
    min_amount = fields.Float('Monto Minimo')
    max_amount = fields.Float('Monto Máximo', help='Si no tiene monto máximo, dejar en 0')
