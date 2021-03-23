from odoo import models

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def create(self, vals_list):
        for vals in vals_list:
            if vals.sale_id:
                sale_order = self.env['sale.order'].search([('id','=',vals.sale_id.id)])
                if sale_order.l10n_latam_document_type_id:
                    vals.l10n_latam_document_type_id = sale_order.l10n_latam_document_type_id.id

        return super(AccountInvoice, self).create(vals_list)
