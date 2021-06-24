from odoo import models, fields, api
from odoo.tools.translate import _


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    is_jump_number = fields.Boolean('Se omitiran folios')

    document_number = fields.Char('Número de Documento')

    document_type_id = fields.Many2one('l10n_latam.document.type', "Tipo de Documento",domain=[('code','in',['61','56'])])

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res.update({
            'is_jump_number' : self.is_jump_number,
            'document_number': self.document_number,
            'l10n_latam_document_type_id': self.l10n_latam_document_type_id.id if not self.document_type_id else self.document_type_id.id,
            'l10n_latam_document_number': self.l10n_latam_document_number,
        })
        return res

    @api.onchange('l10n_latam_document_number', 'l10n_latam_document_type_id')
    def _onchange_l10n_latam_document_number(self):
        if not self.document_type_id:
            if self.l10n_latam_document_type_id:
                l10n_latam_document_number = self.l10n_latam_document_type_id._format_document_number(
                    self.l10n_latam_document_number)
                if self.l10n_latam_document_number != l10n_latam_document_number:
                    self.l10n_latam_document_number = l10n_latam_document_number
