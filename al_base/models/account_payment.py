from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    check_number = fields.Char('Número de Cheque')

    bank_name = fields.Char('Banco',related='partner_bank_id.bank_id.name')