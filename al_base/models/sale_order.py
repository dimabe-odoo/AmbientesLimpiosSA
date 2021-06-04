from odoo import models, fields, api
from datetime import datetime, timedelta
from ..utils.get_range_to_approve import get_range_discount
from ..utils.calculate_business_day_dates import calculate_business_day_dates
from ..utils.roundformat_clp import round_clp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('todiscountapprove', 'Por Aprobación de Descuento'), ('toconfirm', 'Por Aprobar Cobranza')])

    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string="Tipo de Documento",
                                                  default=lambda self: self.env['l10n_latam.document.type'].search(
                                                      [('code', '=', 33)]), required=True)

    request_date = fields.Datetime('Fecha de solicitud')

    discount_approve_date = fields.Datetime('Fecha de aprobación de Descuento')

    confirm_date = fields.Datetime('Fecha de aprobación desde Cobranza')

    invisible_btn_confirm = fields.Boolean(compute="_compute_invisible_btn_confirm", default=False)

    amount_discount = fields.Float(compute="_compute_amount_discount")

    @api.onchange('user_id')
    def on_change_user(self):
        for item in self:
            clients = self.env['res.partner'].search([('user_id', '=', item.user_id.id)])
            if clients:
                res = {
                    'domain': {
                        'partner_id': [('user_id', '=', item.user_id.id)],
                        'partner_shipping_id': [('user_id', '=', item.user_id.id)]
                    }
                }
            else:
                res = {
                    'domain': {
                        'partner_id': ['|', ('company_id', '=', False),
                                       ('company_id', '=', self.env.user.company_id.id)]
                    }
                }
            return res

    @api.model
    def _compute_amount_discount(self):
        for item in self:
            item.amount_discount = (item.amount_undiscounted - (item.amount_total - item.amount_tax))

    def send_message(self, partner_list, approve_type):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        body = f'<p>Estimados.<br/><br/>Se ha generado una nueva órden de venta <a href="{base_url}/web#id={self.id}&action=343&model=sale.order&view_type=form&cids=&menu_id=229">{self.name}</a>. La cual requiere aprobación por {approve_type}<br/></p>Atte,<br/>{self.company_id.name}'
        subject = f'Nueva órden de venta - Aprobar por {approve_type}'
        self.message_post(author_id=2, subject=subject, body=body, partner_ids=partner_list)

    def order_to_discount_approve(self):
        if self.l10n_latam_document_type_id.code == "33":
            if (self.state == 'draft' or self.state == 'sent') and self.get_range_discount():
                self.state = 'todiscountapprove'
                self.request_date = datetime.today()
                user_list = self.get_partners_by_range(self.get_range_discount())
                self.send_message(user_list, 'Descuento')
            elif self.state == 'todiscountapprove' or not self.get_range_discount():
                self.state_to_toconfirm()
        else:
            self.action_confirm()

    def state_to_toconfirm(self):
        if not self.invisible_btn_confirm:
            self.write({
                'state': 'toconfirm',
                'discount_approve_date': datetime.today()
            })
            partner_list = self.get_partner_to()
            self.send_message(partner_list, 'Cobranza')
        else:
            raise models.ValidationError(
                'Usted no tiene los permisos correspondientes para aprobar por Descuento el Pedido de Venta')

    def action_confirm(self):
        if self.env.user.partner_id.id not in self.get_partner_to() and self.state == 'toconfirm':
            raise models.ValidationError(
                'Usted no tiene los permisos correspondientes para aprobar por Cobranza el Pedido de Venta')
        else:
            res = super(SaleOrder, self).action_confirm()
            self.confirm_date = datetime.today()
            return res

    # Grupo Cobranza
    @api.model
    def get_partner_to(self):
        user_group = self.env.ref('al_base.group_order_confirmation')
        partner_list = [
            usr.partner_id.id for usr in user_group.users if usr.partner_id
        ]
        return partner_list

    @api.model
    def _compute_invisible_btn_confirm(self):
        for item in self:
            if item.state == 'todiscountapprove' or item.state == 'draft' or item.state == 'sent':
                if item.get_range_discount():
                    user_can_access = False
                    if item.env.user in item.get_range_discount().user_ids:
                        user_can_access = True
                    item.invisible_btn_confirm = not user_can_access
                else:
                    item.invisible_btn_confirm = False
            else:
                item.invisible_btn_confirm = True

    def get_partners_by_range(self, range):
        user_list = [
            usr.partner_id.id for usr in range.user_ids if usr.partner_id
        ]
        return user_list

    @api.model
    def get_range_discount(self):
        approve_sale_ids = self.env['custom.range.approve.sale'].sudo().search([])
        return get_range_discount(approve_sale_ids, self.amount_discount)

    @api.model
    def get_email_to_discount_approve(self):
        approve_sale_id = self.get_range_discount()
        if len(approve_sale_id) > 0:
            email_list = [
                usr.partner_id.email for usr in approve_sale_id.user_ids if usr.partner_id.email
            ]
            return ','.join(email_list)

    @api.onchange('date_order')
    def _onchange_date_order(self):
        for item in self:
            item.validity_date = calculate_business_day_dates(item.date_order, 2)

    def roundclp(self, value):
        return round_clp(value)

    def _get_custom_report_name(self):
        return '%s %s' % ('Nota de Venta - ', self.name)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, values):
        if 'order_id' in values.keys():
            product_ids = self.env['sale.order.line'].search([('order_id', '=', values['order_id'])]).mapped(
                'product_id')
            if len(product_ids) > 0:
                if 'product_id' in values.keys() and 'name' in values.keys():
                    if values['product_id'] in product_ids.ids:
                        raise models.ValidationError(
                            'No puede agregar el producto {} más de una vez'.format(values['name']))

        return super(SaleOrderLine, self).create(values)
