from odoo import fields, models, api
from dateutil.relativedelta import relativedelta as relative
from odoo.tools.config import config
from datetime import date, datetime
from dateutil import relativedelta
from py_linq import Enumerable


class CustomLoan(models.Model):
    _name = 'custom.loan'
    _description = 'Prestamo'
    _inherit = ['mail.thread']

    display_name = fields.Char('Nombre a mostrar')

    type_of_loan = fields.Selection([('new', 'Nuevo'), ('in_process', 'En proceso')], default='new',
                                    string='Tipo de Prestamo', required=True)

    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)

    fee_qty = fields.Integer('Cantidad de Cuota', track_visibility='onchange')

    fee_value = fields.Monetary('Valor de Cuota', track_visibility='onchange')

    fee_remaining = fields.Integer('Cuota Restantes', track_visibility='onchange')

    loan_total = fields.Monetary('Total a prestar', track_visibility='onchange')

    currency_id = fields.Many2one('res.currency', string='Moneda',
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'CLP')]))

    date_start = fields.Date(default=datetime.today())

    date_start_old = fields.Date()

    interest = fields.Float('Interes')

    fee_ids = fields.One2many('custom.fee', 'loan_id')

    next_fee_id = fields.Many2one('custom.fee', compute='compute_next_fee')

    next_fee_date = fields.Date('Proxima Cuota', related='next_fee_id.expiration_date')

    rule_id = fields.Many2one('hr.salary.rule', string='Regla', domain=[('discount_in_fee', '=', True)])

    indicator_id = fields.Many2one('custom.indicators', string="Indicador que se inciara")

    state = fields.Selection([('draft', 'Borrador'), ('in_process', 'En Proceso'), ('done', 'Finalizado')],
                             default='draft', track_visibility='onchan ge')

    def compute_fee_remaining(self):
        for item in self:
            if item.state == 'in_process':
                item.fee_remaining = len(item.fee_ids.filtered(lambda a: not a.paid))
            else:
                item.fee_remaining = 0

    def compute_next_fee(self):
        for item in self:
            if len(item.fee_ids.filtered(lambda a: not a.paid)) > 0 and item.state != 'done':
                item.next_fee_id = item.fee_ids.filtered(lambda a: not a.paid)[0]
            else:
                item.next_fee_id = None

    def write(self, values):
        if 'fee_value' in values.keys():
            if values['fee_value'] == 0:
                raise models.ValidationError('El valor de la cuota debe ser mayor a 0')
        if self.type_of_loan == 'in_process' and self.state != 'done' and self.verify_is_complete():
            values['state'] = 'done'
        res = super(CustomLoan, self).write(values)

        return res

    def recalculate_loan(self):
        for fee in self.fee_ids:
            fee.unlink()
        if self.type_of_loan == 'new':
            data = self.calculate_fee(fee_value=self.fee_value, type_of_loan=self.type_of_loan,
                                      date_start=self.date_start, qty=self.fee_qty)
        else:
            months = self.get_months_diff(date1=self.date_start_old, date2=self.date_start)
            data = self.calculate_fee(fee_value=self.fee_value, type_of_loan=self.type_of_loan,
                                      date_start=self.date_start, qty=self.fee_qty, date_start_old=self.date_start_old,
                                      months=months)
        self.write({
            'loan_total': data['total']
        })
        for fee in data['fees']:
            fee.write({
                'loan_id': self.id
            })
        self.verify_is_complete()

    def verify_is_complete(self):
        if all(self.fee_ids.mapped('paid')):
            return True
        else:
            return False

    @api.model
    def create(self, values):
        if values['fee_value'] == 0:
            raise models.ValidationError('El valor de la cuota debe ser mayor a 0')
        date_start = datetime.strptime(values['date_start'], '%Y-%m-%d').date()
        if values['type_of_loan'] == 'in_process':
            date_start_old = datetime.strptime(values['date_start_old'], '%Y-%m-%d').date()

            if date_start_old > date.today():
                raise models.UserError('La fecha de primer pago no puede ser mayor al dia actual')
            months = self.get_months_diff(date_start_old, date_start)
            data = self.calculate_fee(fee_value=values['fee_value'], type_of_loan=values['type_of_loan'],
                                      date_start=date_start, qty=values['fee_qty'],
                                      date_start_old=date_start_old, months=months)
            values['loan_total'] = round(data['total'])
        else:
            data = self.calculate_fee(fee_value=values['fee_value'], type_of_loan=values['type_of_loan'],
                                      date_start=date_start, qty=values['fee_qty'])
            values['loan_total'] = round(data['total'])
        res = super(CustomLoan, self).create(values)
        for fee in data['fees']:
            fee.write({
                'loan_id': res.id
            })
        if res.type_of_loan == 'in_process':
            res.message_post(
                body=f"Se creado prestamo que se encuentra en proceso , la cual se encuentra en la cuota N° {res.next_fee_id.number}")
        if self.verify_is_complete() and res.type_of_loan == 'in_process':
            res.state = 'done'
        return res

    def get_months_diff(self, date1, date2):
        r = relativedelta.relativedelta(date2, date1)
        print(r)
        months = r.months + (r.years * 12)
        return months

    def button_confirm(self):
        for item in self:
            item.write({
                'state': 'in_process'
            })

    def calculate_fee(self, fee_value, date_start, type_of_loan, qty, date_start_old=None, months=0):
        index = 0
        remaing = 0
        fee_list = []
        for fee in range(qty):
            fee = self.env['custom.fee'].create({
                'value': fee_value,
                'expiration_date': date_start + relative(
                    months=index) if type_of_loan == 'new' else date_start_old + relative(
                    months=index),
                'number': index + 1,
                'paid': type_of_loan == 'in_process' and remaing <= months + 1
            })
            fee_list.append(fee)
            remaing += 1
            index += 1
        total = []
        for fee in fee_list:
            total.append(fee.value)
        return {'total': sum(total), 'fees': fee_list}
