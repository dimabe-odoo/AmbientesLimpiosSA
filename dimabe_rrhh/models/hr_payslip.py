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

    loan_ids = fields.Many2many('custom.loan')

    personal_movement_ids = fields.One2many('custom.personal.movements', 'payslip_id')

    fee_id = fields.Many2one('custom.fee', string='Cuota Pagada')

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

    def update_other_entries(self):
        self.get_permanent_discounts()
        loan_id = self.env['custom.loan'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'in_process'),
             ('rule_id.code', 'not in', self.input_line_ids.mapped('code'))])
        loan_id = loan_id.filtered(lambda a: self.date_from <= a.next_fee_date <= self.date_to)
        loans = []
        for loan in loan_id:
            if not self.input_line_ids.filtered(lambda a: a.code == loan.rule_id.code and a.amount > 0):
                type_id = self.env['hr.payslip.input.type'].search([('code', '=', loan.rule_id.code)])
                actual_fee = len(loan_id.fee_ids.filtered(lambda a: a.paid)) + 1
                if type_id:
                    self.env['hr.payslip.input'].create({
                        'additional_info': f'Cuota {actual_fee}/{loan.fee_qty}',
                        'code': loan.rule_id.code,
                        'contract_id': self.contract_id.id,
                        'payslip_id': self.id,
                        'amount': loan.next_fee_id.value,
                        'input_type_id': type_id.id
                    })
                else:
                    input_type = self.env['hr.payslip.input.type'].create({
                        'name': loan.rule_id.name,
                        'code': loan.rule_id.code
                    })
                    self.env['hr.payslip.input'].create({
                        'additional_info': f'Cuota {actual_fee}/{loan.fee_qty}',
                        'code': loan.rule_id.code,
                        'contract_id': self.contract_id.id,
                        'payslip_id': self.id,
                        'amount': loan.next_fee_id.value,
                        'input_type_id': input_type.id
                    })
                loans.append(loan.id)
            self.write({
                'loan_ids': [(4, l) for l in loans]
            })


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
                        'state': 'done'
                    })
            return super(HrPaySlip, self).action_payslip_done()

    def get_permanent_discounts(self):
        if self.contract_id and len(self.contract_id.permanent_discounts_ids) > 0:
            for item in self.contract_id.permanent_discounts_ids:
                exist_input = self.exist_input(item.salary_rule_id.code)
                if not exist_input:

                    type_id = self.env['hr.payslip.input.type'].search([('code', '=', item.salary_rule_id.code)])
                    if type_id:
                        self.env['hr.payslip.input'].create({
                            'additional_info': 'Descuento Fijo',
                            'code': item.salary_rule_id.code,
                            'contract_id': self.contract_id.id,
                            'payslip_id': self.id,
                            'input_type_id': type_id.id,
                            'amount': item.amount
                        })
                    else:
                        input_type = self.env['hr.payslip.input.type'].create({
                            'name': item.salary_rule_id.name,
                            'code': item.salary_rule_id.code
                        })

                        self.env['hr.payslip.input'].create({
                            'additional_info': 'Descuento Fijo',
                            'code': item.salary_rule_id.code,
                            'contract_id': self.contract_id.id,
                            'payslip_id': self.id,
                            'input_type_id': input_type.id,
                            'amount': item.amount
                        })
                else:
                    exist_input.write({
                        'amount': item.amount
                    })

    def exist_input(self, salary_rule_code):
        input_type_id = self.env['hr.payslip.input.type'].search([('code', '=', salary_rule_code)])

        if input_type_id:
            payslip_input = self.env['hr.payslip.input'].search(
                [('payslip_id', '=', self._origin.id), ('input_type_id', '=', input_type_id.id)])

            return payslip_input
        else:
            False



class HrPaySlipLine(models.Model):
    _inherit = 'hr.payslip.line'

    def _get_additional_info(self):
        payslip_input = self.env['hr.payslip.input'].search(
            [('code', '=', self.code), ('payslip_id', '=', self.slip_id.id)])
        return f' - {payslip_input.additional_info}' if payslip_input.additional_info else ''
