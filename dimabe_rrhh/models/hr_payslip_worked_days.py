from odoo import models, fields, api

class HrPayslipWorkedDays(models.Model):

    _inherit = 'hr.payslip.worked_days'

    number_of_days = fields.Float(readonly=False)



    @api.onchange('number_of_days')
    def _onchange_pof_days(self):
        for item in self:
            item.amount = item.payslip_id.contract_id.wage / 30 * item.number_of_days
            item.number_of_hours = item.payslip_id.contract_id.resource_calendar_id.full_time_required_hours / item.payslip_id.contract_id.resource_calendar_id.hours_per_day * item.number_of_days

    
