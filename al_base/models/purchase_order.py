from odoo import fields, models, api
from datetime import datetime

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    date_delivered = fields.Date(string='Fecha de Entrega')

    state = fields.Selection(selection_add=[('toamountapprove', 'Por Aprobación de Monto')])

    request_date = fields.Datetime('Fecha de solicitud')

    amount_approve_date = fields.Datetime('Fecha de aprobación de monto')

    invisible_custom_btn_confirm = fields.Boolean(compute="_compute_invisible_custom_btn_confirm", defaul=True)

    def order_to_amount_approve(self):
        if self.state == 'draft':
            self.state = 'toamountapprove'
            self.request_date = datetime.today()
            template_id = self.env.ref('al_base.po_to_amount_approve_mail_template')
            try:
                self.message_post_with_template(template_id.id)
            except Exception as e:
                print(f'Error {e}')

    def button_confirm(self):
        if self.state == 'draft' and self.get_range_amount():
            self.order_to_amount_approve()
        if self.state == 'toamountapprove':
            self.amount_approve_date = datetime.today()
            return super(PurchaseOrder, self).button_confirm()
        if self.state == 'sent':
            res = super(PurchaseOrder, self).button_confirm()
            return res
    @api.model
    def get_email_to_amount_approve(self):
        approve_sale_ids = self.env['custom.range.approve.purchase']
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

    @api.model
    def get_range_amount(self):
        approve_purchase_ids = self.env['custom.range.approve.purchase'].search([])
        approve_purchase_id = 0
        for item in approve_purchase_ids:
            if item.max_amount != 0:
                if item.min_amount <= self.amount_total <= item.max_amount:
                    approve_purchase_id = item.id
                    break
            else:
                if self.amount_total >= item.min_amount:
                    approve_purchase_id = item.id
                    break
        return approve_purchase_ids.filtered(lambda a: a.id == approve_purchase_id)

    @api.model
    def _compute_invisible_custom_btn_confirm(self):
        for item in self:
            if item.state == 'toamountapprove':
                if item.get_range_amount():
                    user_can_access = False
                    if item.env.user in item.get_range_amount().user_ids:
                        user_can_access = True
                    item.invisible_custom_btn_confirm = not user_can_access
                else:
                    item.invisible_custom_btn_confirm = False
            else:
                item.invisible_custom_btn_confirm = False
