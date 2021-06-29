from odoo import fields, models, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    check_number = fields.Char('Número de Cheque')

    check_number_invisible = fields.Boolean(compute="_compute_check_number_invisible")

    bank_id = fields.Many2one('res.bank', 'Banco')


    def _create_payment_vals_from_batch(self, batch_result):
        # OVERRIDE
        payment_vals = super()._create_payment_vals_from_batch(batch_result)
        if self.check_number:
            payment_vals['check_number'] = self.check_number
        if self.bank_id:
            payment_vals['bank_id'] = self.bank_id.id
        return payment_vals


    def _create_payment_vals_from_wizard(self):
        # OVERRIDE
        payment_vals = super()._create_payment_vals_from_wizard()
        if self.check_number:
            payment_vals['check_number'] = self.check_number
        if self.bank_id:
            payment_vals['bank_id'] = self.bank_id.id
        return payment_vals

    @api.depends('journal_id')
    def _compute_check_number_invisible(self):
        for item in self:
            if item.payment_type == 'inbound':
                item.check_number_invisible = True
                if 'chq' in self.journal_id.inbound_payment_method_ids.mapped('code'):
                    item.check_number_invisible = False
            if item.payment_type == 'outbound':
                if 'chq' in self.journal_id.outbound_payment_method_ids.mapped('code'):
                    item.check_number_invisible = False

