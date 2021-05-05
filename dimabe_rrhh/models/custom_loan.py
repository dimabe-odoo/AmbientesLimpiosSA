from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.tools.config import config

class CustomLoan(models.Model):
    _name = 'custom.loan'

    employee_id = fields.Many2one('hr.employee', string='Empleado')

    fee_qty = fields.Integer('Cantidad de Cuota')

    fee_value = fields.Monetary('Valor de Cuota')

    loan_total = fields.Monetary('Total de Prestamo',compute='compute_loan_total')

    currency_id = fields.Many2one('res.currency', string='Moneda',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'CLP')]))

    date_start = fields.Date('Fecha de Inicio')

    interest = fields.Float('Interes')

    fee_ids = fields.One2many('custom.fee','loan_id')

    next_fee_id = fields.Many2one('custom.fee',compute='compute_next_fee')

    next_fee_date = fields.Date('Proxima Cuota',related='next_fee_id.expiration_date')

    rule_id = fields.Many2one('hr.salary.rule', string='Regla',domain=[('discount_in_fee','=',True)])

    def compute_next_fee(self):
        for item in self:
            if len(item.fee_ids) > 0:
                item.next_fee_id = item.fee_ids.filtered(lambda a: not a.paid)[0]
            else:
                item.next_fee_id = None

    def compute_loan_total(self):
        for item in self:
            item.loan_total = sum(item.fee_ids.mapped('value'))

    def calculate_fee(self):
        for item in self:
            index = 1
            for fee in range(item.fee_qty):
                self.env['custom.fee'].create({
                    'loan_id': item.id,
                    'value': item.fee_value,
                    'expiration_date': item.date_start + relativedelta(months=index),
                    'number': index
                })
                index += 1