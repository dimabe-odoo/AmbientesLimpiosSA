from odoo import models, fields, api
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('todiscountapprove', 'Por Aprobación de Descuento'), ('toconfirm', 'Por Aprobar')])

    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string="Tipo de Documento",
                                                  default=lambda self: self.env['l10n_latam.document.type'].search(
                                                      [('code', '=', 33)]), required=True)

    request_date = fields.Datetime('Fecha de solicitud')

    discount_approve_date = fields.Datetime('Fecha de aprobación de Descuento')

    confirm_date = fields.Datetime('Fecha de aprobación desde Cobranza')

    invisible_btn_confirm = fields.Boolean(compute="_compute_invisible_btn_confirm", defaul=True)

    def order_to_discount_approve(self):
        if not self.get_range_amount():
            self.state_to_toconfirm()
        else:
            if self.state == 'draft':
                self.state = 'todiscountapprove'
                self.request_date = datetime.today()
                template_id = self.env.ref('al_base.so_to_amount_approve_mail_template')
                try:
                    self.message_post_with_template(template_id.id)
                except Exception as e:
                    print(f'Error {e}')

    def state_to_toconfirm(self):
        self.state = 'toconfirm'
        self.discount_approve_date = datetime.today()
        template_id = self.env.ref('al_base.so_to_approve_mail_template')
        self.message_post_with_template(template_id.id)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.confirm_date = datetime.today()
        return res

    @api.model
    def get_email_to(self, ref_id):
        user_group = self.env.ref(ref_id)
        email_list = [
            usr.partner_id.email for usr in user_group.users if usr.partner_id.email
        ]
        return ','.join(email_list)

    @api.model
    def _compute_invisible_btn_confirm(self):
        for item in self:
            if item.state == 'todiscountapprove' or item.state == 'draft':
                if item.get_range_discount():
                    user_can_access = False
                    if item.env.user in item.get_range_discount().user_ids:
                        user_can_access = True
                    item.invisible_btn_confirm = not user_can_access
                else:
                    item.invisible_btn_confirm = False
            if item.state == 'toconfirm':
                item.invisible_btn_confirm = True

    @api.model
    def get_range_discount(self):
        approve_sale_ids = self.env['custom.range.approve.sale'].search([])
        approve_sale_id = 0
        amount_discount = (self.amount_undiscounted - (self.amount_total - self.amount_tax))
        for item in approve_sale_ids:
            if item.max_amount != 0:
                if item.min_amount <= amount_discount <= item.max_amount:
                    approve_sale_id = item.id
                    break
            else:
                if amount_discount >= item.min_amount:
                    approve_sale_id = item.id
                    break
        return approve_sale_ids.filtered(lambda a: a.id == approve_sale_id)

    @api.model
    def get_email_to_discount_approve(self):
        approve_sale_ids = self.env['custom.range.approve.sale']
        approve_sale_id = 0
        for item in approve_sale_ids:
            if item.max_amount != 0:
                if self.amount_total >= item.min_amount and self.amount_total <= item.max_amount:
                    approve_sale_id = item.id
                    break
            else:
                if self.amount_total >= item.min_amount:
                    approve_sale_id = item.id
                    break

        email_list = [
            usr.partner_id.email for usr in approve_sale_ids.filtered(lambda a: a.id == approve_sale_id).user_ids if
            usr.email
        ]

        return ','.join(email_list)
