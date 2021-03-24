from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, values):
        if 'sale_line_ids' in values.keys():
            sale_order = self.env['sale.order'].search([('name','=',values['invoice_origin'])])
            raise models.ValidationError('{} {}'.format(sale_order.name, sale_order.l10n_latam_document_type_id.name))
            if sale_order.l10n_latam_document_type_id:
                values['l10n_latam_document_type_id'] = sale_order.l10n_latam_document_type_id.id

        return super(AccountMove, self).create(values)
