from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, values):
        raise models.ValidationError(values.keys())
        if 'sale_line_ids' in values.keys():
            sale_order = self.env['sale.order'].search([('id','=',values['sale_line_ids'])])
            if sale_order.l10n_latam_document_type_id:
                values['l10n_latam_document_type_id'] = sale_order.l10n_latam_document_type_id.id

        return super(AccountMove, self).create(values)
