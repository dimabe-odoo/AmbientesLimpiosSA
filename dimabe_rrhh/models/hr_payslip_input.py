from odoo import fields, models, api


class HrPaySlipInput(models.Model):
    _inherit = 'hr.payslip.input'

    additional_info = fields.Char('Información Adicional')
