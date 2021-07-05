from odoo import models, fields, api
from py_linq import Enumerable
from datetime import datetime, timedelta
from ..utils.get_range_to_approve import get_range_discount
from ..utils.calculate_business_day_dates import calculate_business_day_dates
from ..utils.roundformat_clp import round_clp
from ..utils.generate_notification import send_notification, get_followers


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

    invisible_btn_confirm = fields.Boolean(compute="_compute_invisible_btn_confirm", default=True)

    amount_discount = fields.Float(compute="_compute_amount_discount")

    @api.model
    def create(self, values):
        if isinstance(values, list):
            for value in values:
                if 'client_order_ref' in value.keys():
                    if value['client_order_ref']:
                        client = self.env['sale.order'].search([('client_order_ref', '=', value['client_order_ref'])])
                        if client:
                            raise models.ValidationError(
                                f'No puede crear una nota de venta con la OC {value["client_order_ref"]}')
        else:
            if 'client_order_ref' in values.keys():
                if values['client_order_ref']:
                    client = self.env['sale.order'].search([('client_order_ref', '=', values['client_order_ref'])])
                    if client:
                        raise models.ValidationError(
                            f'No puede crear una nota de venta con la oc {values["client_order_ref"]}')

        return super(SaleOrder, self).create(values)

    def write(self,values):
        if isinstance(values, list):
            for value in values:
                if 'client_order_ref' in value.keys():
                    if value['client_order_ref']:
                        client = self.env['sale.order'].search([('client_order_ref', '=', value['client_order_ref'])])
                        if client:
                            raise models.ValidationError(
                                f'No puede crear una nota de venta con la OC {value["client_order_ref"]}')
        else:
            if 'client_order_ref' in values.keys():
                if values['client_order_ref']:
                    client = self.env['sale.order'].search([('client_order_ref', '=', values['client_order_ref'])])
                    if client:
                        raise models.ValidationError(
                            f'No puede crear una nota de venta con la oc {values["client_order_ref"]}')

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


        return super(SaleOrder, self).action_confirm()

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
                    if item.get_range_discount().user_configuration == 'leader':
                        if item.state == 'draft' or item.state == 'sent':
                            team = self.get_team_by_vendor(item.user_id)
                            if team:
                                if item.env.user in team.mapped('member_ids'):
                                    user_can_access = True
                                else:
                                    if item.env.user in item.get_range_discount().external_user_ids:
                                        user_can_access = True
                            else:
                                if item.env.user in item.get_range_discount().external_user_ids:
                                    user_can_access = True
                                else:
                                    user_can_access = False
                        else:
                            leader = self.get_leader_by_vendor(item.user_id)
                            if leader:
                                if item.env.user == leader:
                                    user_can_access = True
                            else:
                                user_can_access = False
                    elif item.get_range_discount().user_configuration == 'user':
                        if item.state == 'draft' or item.state == 'sent':
                            vendor_group = self.env.ref('al_base.custom_group_vendors')
                            if item.env.user in vendor_group.users:
                                user_can_access = True
                        else:
                            if item.env.user in item.get_range_discount().user_ids:
                                user_can_access = True
                    else:
                        if item.env.user in item.get_range_discount().user_ids:
                            user_can_access = True
                    item.invisible_btn_confirm = not user_can_access
                else:
                    item.invisible_btn_confirm = False
            else:
                item.invisible_btn_confirm = True


    def get_partners_by_range(self, range):
        user_list = []
        if range.user_configuration == 'leader':
            leader_id = self.get_leader_by_vendor(self.user_id)
            user_list.append(leader_id.partner_id.id)
        else:
            user_list = [
                usr.partner_id.id for usr in range.user_ids if usr.partner_id
            ]
        return user_list


    def get_leader_by_vendor(self, vendor):
        team = self.get_team_by_vendor(vendor)
        if team:
            if team.user_id:
                return team.user_id
        else:
            return False


    def get_team_by_vendor(self, vendor):
        sale_team_ids = self.env['crm.team'].search([])

        for team in sale_team_ids:
            if vendor in team.mapped('member_ids'):
                return team
        return False


    @api.model
    def get_range_discount(self):
        approve_sale_ids = self.env['custom.range.approve.sale'].sudo().search([])
        return get_range_discount(approve_sale_ids, self.amount_discount)


    @api.onchange('date_order')
    def _onchange_date_order(self):
        for item in self:
            item.validity_date = calculate_business_day_dates(item.date_order, 2)


    def roundclp(self, value):
        return round_clp(value)


    def _get_custom_report_name(self):
        return '%s %s' % ('Nota de Venta - ', self.name)

    def close_orders(self):
        sale_orders = self.env['sale.order'].search([])
        sale_order_parcial = Enumerable(sale_orders).where(lambda x: len(x.picking_ids) > 1)
        if sale_order_parcial.count() > 0:
            for sale in sale_order_parcial:
                followers = get_followers(self._inherit, sale.id)
                send_notification('Pedido Cerrar', 'Pedido Cerrado por cierre automatico del dia', 2, followers,
                                  self._inherit, sale.id)
                delivery_pending = Enumerable(sale.picking_ids).where(lambda x: x.state != 'done')
                if delivery_pending.count() == 0:
                    continue
                for pending in delivery_pending:
                    followers = get_followers('stock.picking', pending.id)
                    send_notification('Pedido Cancelado', 'Pedido Cancelado por cierre automatico del dia', 2,
                                      followers, 'stock.picking',
                                      pending.id)
                    pending.action_cancel()
                if sale.state != 'done':
                    sale.write({
                        'state': 'done'
                    })


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        list_product_duplicate = ''
        duplicate_count = 0
        product_to_registered = []

        for values in vals_list:
            registered_duplicate = False
            if 'order_id' in values.keys():
                if values['product_id'] in product_to_registered:
                    registered_duplicate = True
                product_to_registered.append(values['product_id'])

                if not self.unique_product_validation(values['order_id'], values, True) or registered_duplicate:
                    if values['name'] not in list_product_duplicate:
                        duplicate_count += 1
                        list_product_duplicate = list_product_duplicate + '\n' + values['name']

        if list_product_duplicate != '':
            raise models.ValidationError('No puede agregar {} más de una vez:\n  {}\n'.format(
                'los siguientes productos' if duplicate_count > 1 else 'el siguiente producto', list_product_duplicate))

        return super().create(vals_list)

    def write(self, values):
        self.unique_product_validation(self.order_id.id, values, False)
        return super(SaleOrderLine, self).write(values)

    def unique_product_validation(self, order, product, create):
        product_ids = self.env['sale.order.line'].search([('order_id', '=', order)]).mapped(
            'product_id')
        if len(product_ids) > 0:
            if 'product_id' in product.keys() and 'name' in product.keys():
                if product['product_id'] in product_ids.ids:
                    if create:
                        return False
                    else:
                        raise models.ValidationError(
                            'No puede agregar el producto {} más de una vez'.format(product['name']))
                else:
                    return True
        else:
            return True
