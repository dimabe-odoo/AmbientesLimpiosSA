from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[('toconfirm', 'Por Aprobar')])

    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string="Tipo de Documento",
                                                  default=lambda self: self.env['l10n_latam.document.type'].search(
                                                      [('code', '=', 33)]),required=True)

    
    def order_to_confirm(self):
        if self.state == 'draft':
            self.state = 'toconfirm'
            template_id = self.env.ref('al_base.so_to_approve_mail_template')
            self.message_post_with_template(template_id.id)

    @api.model
    def get_email_to(self, ref_id):
        user_group = self.env.ref(ref_id)
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email
        ]
        return ','.join(email_list)