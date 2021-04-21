from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string="Tipo de Documento",
                                                  default=lambda self: self.env['l10n_latam.document.type'].search(
                                                      [('code', '=', 33)]),required=True)
