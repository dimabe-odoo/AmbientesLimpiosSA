from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string="Tipo de Documento")


    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.invoice_ids:
            if self.invoice_ids.filtered(lambda x : x.l10n_latam_document_type_id == None):
                self.invoice_ids[-1].write({
                    'l10n_latam_document_type_id': self.l10n_latam_document_type_id.id
                })

