from odoo import models , fields,api
from datetime import date , timedelta
from dateutil.relativedelta import * 
import pandas as pd
from odoo.addons import decimal_precision as dp

class CustomSettlement(models.Model):
    _name = 'custom.settlement'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado',
        required=True
        )

    # company_id = fields.Many2one(
    #     'res.partner',
    #     string='Compañia',
    #     related='employee_id.address_id'
    #     )

    contract_id = fields.Many2one(
        'hr.contract',
        string='Contrato',
        )
    
    fired_id = fields.Many2one(
        'custom.fired',
        string='Causal de Despido',
        )

    article_causal = fields.Selection('Articulo',related='fired_id.article')

    # date_start = fields.Date('Fecha inicio contrato',related='contract_id.date_start')

    date_notification = fields.Date('Fecha notification de despido',default=date.today())

    date_settlement = fields.Date('Fecha finiquito',required=True)

    period_service = fields.Char('Periodo de servicio',compute='compute_perid',readonly=True)

    vacation_days = fields.Float('Dias de Vacaciones',compute='compute_vacation_days',readonly=True)

    day_taken = fields.Float('Dias Tomados',compute='compute_days_takes',default=0.0)

    days_pending = fields.Float('Dias Pendientes',compute='compute_days_pending')

    non_working_days = fields.Integer('Dia Inhabilies',compute='compute_no_working_days')

    type_contract = fields.Selection([('Fijo', 'Fijo'),('Variable','Variable')],default='Fijo')

    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        )

    # wage = fields.Monetary('Sueldo Base',related='contract_id.wage',current_field='currency_id',digits=dp.get_precision('Paypoll'))

    reward_selection = fields.Selection([
        ('Yes', 'Si'),
        ('No', 'No'),
        ('Edit', 'Editar')
    ], string='Gratificacion', default='Yes')

    snack_bonus = fields.Float('Colacion', digits=dp.get_precision('Payroll'))

    mobilization_bonus = fields.Float('Movilizacion', digits=dp.get_precision('Payroll'))

    pending_remuneration_payment = fields.Monetary('Remuneraciones Pendientes', digits=dp.get_precision('Payroll'))

    compensation_warning = fields.Monetary('Indemnización Aviso Previo', compute='compute_warning',
                                           digits=dp.get_precision('Payroll'))

    compensation_years = fields.Monetary('Indemnización Años de Servicio', compute='compute_years',
                                         digits=dp.get_precision('Payroll'))

    compensation_vacations = fields.Monetary('Indemnización Vacaciones', compute='compute_vacations',
                                             digits=dp.get_precision('Payroll'))

    settlement = fields.Monetary('Finiquito', digits=dp.get_precision('Payroll'))

    years = fields.Integer('Años', compute='compute_value_show')

    current_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user)

    def compute_value_show(self):
        for item in self:
            period = relativedelta(item.date_settlement,item.date_start)
            item.years = period.years

    @api.onchange('field')
    def compute_day_pending(self):
        for item in self:
            item.days_pending = (round(item.vacation_days) - item.day_takes) + item.non_working_days
    
    @api.onchange('date_settlement')
    def compute_period(self):
        for item in self:
            period = relativedelta(item.date_settlement, item.date_start_contract)
            item.period_of_service = '{} años , {} meses , {} dias'.format(period.years, period.months,
                                                                           (period.days + 1))
    @api.onchange('date_settlement')
    def compute_vacation_day(self):
        for item in self:
            period = relativedelta(item.date_settlement, item.date_start_contract)
            item.vacation_days = (15 * period.years + (period.months * 1.25 + (period.days + 1) / 30 * 1.25))

    @api.onchange('reward_selection')
    def compute_reward(self):
        for item in self:
            if item.reward_selection == 'Yes' or item.reward_selection == 'Edit':
                item.reward_value = round(item.wage * 0.25)
            else:
                item.reward_value = 0

    def compute_vacations(self):
        for item in self:
            daily = (item.wage + item.reward_value) / 30
            item.compensation_vacations = round(item.days_pending * daily)

    @api.onchange('date_of_notification')
    def compute_warning(self):
        for item in self:
            if item.date_settlement:
                warning = abs(self.date_of_notification - self.date_settlement).days
                if warning < 30:
                    item.compensation_warning = round(
                        (item.wage + item.reward_value) + (item.snack_bonus + item.mobilization_bonus))

    @api.onchange('date_settlement')
    def compute_years(self):
        for item in self:
            period = relativedelta(item.date_settlement, item.date_start_contract)
            item.compensation_years = round((item.wage + item.reward_value) + (
                    item.snack_bonus + item.mobilization_bonus)) * period.years

    @api.onchange('date_settlement')
    def compute_no_working_days(self):
        for item in self:
            item.non_working_days = item.get_weekend()

    @api.depends('date_settlement', 'pending_remuneration_payment', 'reward_selection')
    def calculate_settlement(self):
        for item in self:
            period = relativedelta(item.date_settlement, item.date_start_contract)
            item.settlement = (item.wage + item.reward_value) + item.pending_remuneration_payment + \
                              (item.snack_bonus + item.mobilization_bonus) \
                              + (item.compensation_vacations + item.compensation_warning + item.compensation_years)

    @api.depends('date_settlement')
    def compute_days_takes(self):
        for item in self:
            payslip = self.env['hr.payslip'].search(
                [('date_from', '>', item.date_start_contract), ('date_from', '<', item.date_settlement),
                 ('contract_id', '=', item.contract_id.id)])
            vacation = payslip.mapped('worked_days_line_ids').filtered(lambda a: 'Vacaciones' in a.name).mapped(
                'number_of_days')
            item.day_takes = sum(vacation)

    @api.onchange('date_settlement')
    def onchange_method(self):
        for item in self:
            payslip = self.env['hr.payslip'].search(
                [('date_from', '>', item.date_start_contract), ('date_from', '<', item.date_settlement),
                 ('contract_id', '=', item.contract_id.id)])
            vacation = payslip.mapped('worked_days_line_ids').filtered(lambda a: 'Vacaciones' in a.name).mapped(
                'number_of_days')
            item.day_takes = sum(vacation)

    def button_done(self):
        for item in self:
            item.write({
                'state': 'done'
            })
            item.contract_id.write({
                'state': 'cancel',
                'active': False
            })

    def test(self):
        payslip = self.env['hr.payslip'].search(
            [('date_from', '>', self.date_start_contract), ('date_from', '<', self.date_settlement),
             ('contract_id', '=', self.contract_id.id)])
        vacation = payslip.mapped('worked_days_line_ids').filtered(lambda a: 'Vacaciones' in a.name).mapped(
            'number_of_days')
        raise models.ValidationError(sum(vacation))

    def get_weekend(self):
        if self.date_settlement:
            days = round(self.vacation_days)
            date_after = self.date_settlement + timedelta(days=days)
            date_settlement = self.date_settlement + timedelta(days=1)
            saturdays = pd.date_range(start=date_settlement, end=date_after, freq='W-SAT').strftime('%m/%d/%Y').tolist()
            models._logger.error(saturdays)
            sundays = pd.date_range(start=date_settlement, end=date_after, freq='W-SUN').strftime('%m/%d/%Y').tolist()
            models._logger.error(sundays)
            holiday = self.env['custom.holidays'].search([('date', '>', date_settlement), ('date', '<', date_after)])
            weeekend = sorted(sorted(saturdays) + sorted(sundays))
            return len(weeekend) + len(holiday)