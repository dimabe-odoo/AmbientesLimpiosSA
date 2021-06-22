from odoo import fields, models, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    check_number = fields.Char('Número de Cheque')

    check_number_invisible = fields.Boolean(compute="_compute_check_number_invisible")


    def _create_payment_vals_from_batch(self, batch_result):
        # OVERRIDE
        payment_vals = super()._create_payment_vals_from_batch(batch_result)
        payment_vals['check_number'] = self.check_number
        return payment_vals


    def _create_payment_vals_from_wizard(self):
        # OVERRIDE
        payment_vals = super()._create_payment_vals_from_wizard()
        payment_vals['check_number'] = self.check_number
        return payment_vals

    @api.depends('journal_id')
    def _compute_check_number_invisible(self):
        for item in self:
            item.check_number_invisible = True
            if 'chq' in self.journal_id.inbound_payment_method_ids.mapped('code'):
                item.check_number_invisible = False

