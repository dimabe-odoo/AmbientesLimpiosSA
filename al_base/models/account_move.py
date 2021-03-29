from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, values):
        
        if values['invoice_origin']:
            sale_order = self.env['sale.order'].search([('name','=',values['invoice_origin'])])
            if sale_order.l10n_latam_document_type_id:
                values['journal_id'] = 1
                values['l10n_latam_document_type_id'] = sale_order.l10n_latam_document_type_id.id
        return super(AccountMove, self).create(values)
