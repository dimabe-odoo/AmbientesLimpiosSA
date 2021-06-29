from odoo import fields, models, api

class HrDepartment(models.Model):
    _inherit = 'hr.department'
    analytic_account_id = fields.Many2one('account.analytic.account', 'Centro de Costos')


    def write(self, values):
        test = super(HrDepartment, self).write(values)
        return test

    @api.model
    def create(self, values):
        test = super(HrDepartment, self).create(values)
        return test

    def unlink(self):
        test = super().unlink()
        return test

