from odoo import models, fields, api


class HrPaySlip(models.Model):
    _inherit = 'hr.payslip'

    worked_days_line_ids = fields.One2many('hr.payslip.worked_days', 'payslip_id', states={'draft': [('readonly', False)], 'verify': [('readonly', False)]})

    indicator_id = fields.Many2one('custom.indicators', string='Indicadores')

    salary_id = fields.Many2one('hr.salary.rule', 'Agregar Entrada')
    
    account_analytic_id = fields.Many2one('account.analytic.account','Centro de Costo',readonly=True)

    basic_salary = fields.Char('Sueldo Base', compute="_compute_basic_salary")

    net_salary = fields.Char('Alcance Liquido', compute="_compute_net_salary")

    personal_movements = fields.Selection((('0', 'Sin Movimiento en el Mes'),
     ('1', 'Contratación a plazo indefinido'),
     ('2', 'Retiro'),
     ('3', 'Subsidios (L Médicas)'),
     ('4', 'Permiso Sin Goce de Sueldos'),
     ('5', 'Incorporación en el Lugar de Trabajo'),
     ('6', 'Accidentes del Trabajo'),
     ('7', 'Contratación a plazo fijo'),
     ('8', 'Cambio Contrato plazo fijo a plazo indefinido'),
     ('11', 'Otros Movimientos (Ausentismos)'),
     ('12', 'Reliquidación, Premio, Bono')     
     ), 'Movimientos Personal', default="0")

    @api.model
    def _compute_basic_salary(self):
        for item in self:
            item.basic_salary = f"$ {int(item.line_ids.filtered(lambda a: a.code=='SUELDO').total)}"

    @api.model
    def _compute_net_salary(self):
        for item in self:
            item.net_salary = f"$ {int(item.line_ids.filtered(lambda a: a.code=='LIQ').total)}"

    def add(self):
        for item in self:
            if item.salary_id:
                type_id = self.env['hr.payslip.input.type'].search([('code','=',item.salary_id.code)])
                amount = 0
                
                if type_id:
                    if item.salary_id.amount_select == 'fix':
                        amount = item.salary_id.amount_fix
                    elif item.salary_id.code == 'COL':
                        if item.contract_id.collation_amount > 0:
                            amount = item.contract_id.collation_amount
                        else:
                            raise models.ValidationError('No se puede agregar Asig. Colación ya que está en 0 en el contrato')
               
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
                        'name': item.salary_id.name. capitalize(),
                        'code': item.salary_id.code,
                        'contract_id': item.contract_id.id,
                        'payslip_id': item.id,
                        'input_type_id': input_type.id
                    })
            item.salary_id = None
    
    @api.model
    def _get_worked_day_lines(self):
        res = super(HrPaySlip, self)._get_worked_day_lines()
        temp = 0 
        days = 0
        attendances = {}
        leaves = []
        if len(res) > 0:
            for line in res:
                if line.get('code') == 'WORK100':
                    attendances = line
                else:
                    leaves.append(line)
            for leave in leaves:
                temp += leave.get('number_of_days') or 0
        attendances['number_of_days'] = days
        attendances['work_entry_type_id'] = 1
        attendances['amount'] = self.contract_id.wage
        res = []
        res.append(attendances)
        res.extend(leaves)
        return res

    