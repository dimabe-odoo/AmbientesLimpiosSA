from odoo import fields, models, api
from ..utils.valid_range_approve import valid_range

class CustomRangeApprovePurchase(models.Model):
    _name = 'custom.range.approve.purchase'

    name = fields.Char('Nombre')
    user_ids = fields.Many2many('res.users', string='Usuarios')
    min_amount = fields.Integer('Monto Minimo')
    max_amount = fields.Integer('Monto Máximo', help='Si no tiene monto máximo, dejar en 0')

    @api.model
    def create(self, values):
        if values['max_amount'] > values['min_amount'] or values['max_amount'] == 0:
            if self.valid_range(values):
                return super(CustomRangeApprovePurchase, self).create(values)
        else:
            raise models.ValidationError('Monto máximo debe ser mayor que el monto mínimo, excepto si el monto máximo no tiene límite, éste debe ser 0')

    def write(self, values):
        if 'max_amount' in values.keys() and 'min_amount' not in values.keys():
            values['min_amount'] = self.min_amount
        if 'max_amount' not in values.keys() and 'min_amount' in values.keys():
            values['max_amount'] = self.max_amount
        if 'max_amount' in values.keys() and 'min_amount' in values.keys():
            if values['max_amount'] > values['min_amount'] or values['max_amount'] == 0:
                if self.valid_range(values):
                    return super(CustomRangeApprovePurchase, self).write(values)
            else:
                raise models.ValidationError('Monto máximo debe ser mayor que el monto mínimo, excepto si el monto máximo no tiene límite, éste debe ser 0')

    def valid_range(self, values):
        range_ids = self.env['custom.range.approve.purchase'].search([])
        valid_range(values, range_ids)


