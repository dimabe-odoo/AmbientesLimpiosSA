from odoo import models, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, values):
        for vals in values:
            if vals.sale_id:
                sale_order = self.env['sale.order'].search([('id','=',vals.sale_id.id)])
                if sale_order.l10n_latam_document_type_id:
                    vals.l10n_latam_document_type_id = sale_order.l10n_latam_document_type_id.id

        return super(AccountInvoice, self).create(values)
