from odoo import fields, models, api


class ModelName(models.Model):
    _name = 'custom.fee'

    number = fields.Integer('Numero')

    value = fields.Monetary('Valor')

    paid = fields.Boolean('Pagado')

    currency_id = fields.Many2one('res.currency', string='Moneda',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'CLP')]))

    expiration_date = fields.Date('Fecha de Vencimiento')

    loan_id = fields.Many2one('custom.loan')

    @api.model
    def write(self,values):
        if all(self.loan_id.fee_ids.mapped('paid')):
            values['state'] = 'done'


