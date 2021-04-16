from odoo import models, fields, api

class HrPayslipWorkedDays(models.Model):

    _inherit = 'hr.payslip.worked_days'

    number_of_days = fields.Float(readonly=False)