from odoo import models, fields, api
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[('toconfirm', 'Por Aprobar')])

    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string="Tipo de Documento",
                                                  default=lambda self: self.env['l10n_latam.document.type'].search(
                                                      [('code', '=', 33)]),required=True)

    request_date = fields.Datetime('Fecha de solicitud')

    approve_date = fields.Datetime('Fecha de aprovación')

    
    def order_to_confirm(self):
        if self.state == 'draft':
            self.state = 'toconfirm'
            self.request_date = datetime.today()
            template_id = self.env.ref('al_base.so_to_approve_mail_template')
            self.message_post_with_template(template_id.id)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.approve_date = datetime.today()
        return res

    @api.model
    def get_email_to(self, ref_id):
        user_group = self.env.ref(ref_id)
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email
        ]
        return ','.join(email_list)