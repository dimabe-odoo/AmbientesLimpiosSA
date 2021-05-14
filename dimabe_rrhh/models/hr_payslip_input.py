from odoo import fields, models, api


class HrPaySlipInput(models.Model):
    _inherit = 'hr.payslip.input'

    info_loan = fields.Char('Informacion de Cuota')
