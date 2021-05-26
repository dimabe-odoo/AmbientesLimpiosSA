from odoo import models, fields, api


class HrPaySlip(models.Model):
    _inherit = 'hr.payslip'

    indicator_id = fields.Many2one('custom.indicators', string='Indicadores', required=True)

    salary_id = fields.Many2one('hr.salary.rule', 'Agregar Entrada')

    account_analytic_id = fields.Many2one('account.analytic.account', 'Centro de Costo', readonly=True)

    basic_salary = fields.Char('Sueldo Base', compute="_compute_basic_salary")

    net_salary = fields.Char('Alcance Liquido', compute="_compute_net_salary")

    worked_days_line_ids = fields.One2many(readonly=False)

    payment_term_id = fields.Many2one('custom.payslip.payment.term', 'Forma de Pago')

    loan_id = fields.Many2one('custom.loan')

    personal_movement_ids = fields.One2many('custom.personal.movements','payslip_id')

    @api.model
    def _compute_basic_salary(self):
        for item in self:
            item.basic_salary = f"$ {int(item.line_ids.filtered(lambda a: a.code == 'SUELDO').total)}"

    @api.model
    def _compute_net_salary(self):
        for item in self:
            item.net_salary = f"$ {int(item.line_ids.filtered(lambda a: a.code == 'LIQ').total)}"

    def add(self):
        for item in self:
            if item.salary_id:
                type_id = self.env['hr.payslip.input.type'].search([('code', '=', item.salary_id.code)])
                amount = 0

                if type_id:
                    if item.salary_id.amount_select == 'fix':
                        amount = item.salary_id.amount_fix
                    elif item.salary_id.code == 'COL':
                        if item.contract_id.collation_amount > 0:
                            amount = item.contract_id.collation_amount
                        else:
                            raise models.ValidationError(
                                'No se puede agregar Asig. Colación ya que está en 0 en el contrato')

                    self.env['hr.payslip.input'].create({
                        'name': item.salary_id.name,
                        'code': item.salary_id.code,
                        'contract_id': item.contract_id.id,
                        'payslip_id': item.id,
                        'input_type_id': type_id.id,
                        'amount': amount
                    })
                else:
                    input_type = self.env['hr.payslip.input.type'].create({
                        'name': item.salary_id.name,
                        'code': item.salary_id.code
                    })
                    self.env['hr.payslip.input'].create({
                        'name': item.salary_id.name.capitalize(),
                        'code': item.salary_id.code,
                        'contract_id': item.contract_id.id,
                        'payslip_id': item.id,
                        'input_type_id': input_type.id
                    })
            item.salary_id = None

    def compute_sheet(self):
        loan_id = self.env['custom.loan'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'in_process'),('rule_id.code','not in',self.input_line_ids.mapped('code'))])
        loan_id = loan_id.filtered(lambda a: self.date_from <= a.next_fee_date <= self.date_to)
        if not self.input_line_ids.filtered(lambda a: a.code == loan_id.rule_id.code and a.amount > 0) and loan_id:
            type_id = self.env['hr.payslip.input.type'].search([('code', '=', loan_id.rule_id.code)])
            if type_id:
                self.env['hr.payslip.input'].create({
                    'name': loan_id.rule_id.name,
                    'code': loan_id.rule_id.code,
                    'contract_id': self.contract_id.id,
                    'payslip_id': self.id,
                    'amount': loan_id.next_fee_id.value,
                    'input_type_id': type_id.id
                })
            else:
                input_type = self.env['hr.payslip.input.type'].create({
                    'name': loan_id.rule_id.name,
                    'code': loan_id.rule_id.code
                })
                self.env['hr.payslip.input'].create({
                    'name': loan_id.rule_id.name,
                    'code': loan_id.rule_id.code,
                    'contract_id': self.contract_id.id,
                    'payslip_id': self.id,
                    'amount': loan_id.next_fee_id.value,
                    'input_type_id': input_type.id
                })

            self.write({
                'loan_id': loan_id.id
            })
        return super(HrPaySlip, self).compute_sheet()

    def action_payslip_done(self):
        for item in self:

            if item.loan_id:
                item.write({
                    'fee_id': item.loan_id.next_fee_id.id,
                })
                item.loan_id.next_fee_id.write({
                    'paid': True,
                })

                if item.loan_id.verify_is_complete():
                    item.loan_id.write({
                        'state':'done'
                    })
            return super(HrPaySlip, self).action_payslip_done()

    # @api.model
    # def _get_worked_day_lines(self):
    #    res = super(HrPaySlip, self)._get_worked_day_lines()
    #    temp = 0 
    #    days = 0
    #    attendances = {}
    #    leaves = []
    #    if len(res) > 0:
    #        for line in res:
    #            if line.get('code') == 'WORK100':
    #                attendances = line
    #           else:
    #                leaves.append(line)
    #        for leave in leaves:
    #            temp += leave.get('number_of_days') or 0
    #    attendances['number_of_days'] = days
    #    attendances['work_entry_type_id'] = 1
    #    attendances['amount'] = self.contract_id.wage
    #    res = []
    #    res.append(attendances)
    #    res.extend(leaves)
    #    return res
