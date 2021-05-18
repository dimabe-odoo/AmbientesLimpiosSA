from odoo import fields, models, api
from datetime import datetime
from ..utils.get_range_to_approve import get_range_amount

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
            user_list = self.get_partners_by_range(self.get_range_amount())
            self.send_message(user_list, 'Monto')


    def send_message(self, partner_list, approve_type):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        body = f'<p>Estimados.<br/><br/>Se ha generado una nueva órden de compra <a href="{base_url}/web#id={self.id}&action=432&model=purchase.order&view_type=form&cids=&menu_id=300">{self.name}</a>. La cual requiere aprobación por Monto'
        subject = f'Nueva órden de compra - Aprobar por {approve_type}'
        self.message_post(author_id=2, subject=subject, body=body, partner_ids=partner_list)


    def button_confirm(self):
        if self.state == 'draft' and self.get_range_amount():
            self.order_to_amount_approve()
        elif self.state == 'toamountapprove':
            if not self.invisible_custom_btn_confirm:
                self.write({'state': 'to approve', 'amount_approve_date': datetime.today()})
                return super(PurchaseOrder, self).button_confirm()
            else:
                raise models.ValidationError('Usted no tiene los permisos correspondientes para aprobar por monto el Pedido de Compra')
        else:
            return super(PurchaseOrder, self).button_confirm()



    @api.model
    def get_partner_to_amount_approve(self):
        approve_purchase_id = self.get_range_amount()
        if len(approve_purchase_id) > 0:
            email_list = [
                usr.partner_id.id for usr in approve_purchase_id.user_ids if usr.partner_id
            ]
            return ','.join(email_list)

    def get_partners_by_range(self, range):
        user_list = [
            usr.partner_id.id for usr in range.user_ids if usr.partner_id
        ]
        return user_list

    @api.model
    def get_range_amount(self):
        approve_purchase_ids = self.env['custom.range.approve.purchase'].search([])
        return get_range_amount(approve_purchase_ids, self.amount_total)

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


    @api.model
    def _get_picking_type(self, company_id):
        self.picking_type_id = None
        return None
