import datetime

from odoo import models, fields, api


class RouteMapLine(models.Model):
    _name = 'route.map.line'
    _rec_name = 'display_name'

    display_name = fields.Char('Nombre a mostrar', compute='compute_display_name')

    map_id = fields.Many2one('route.map', string='Hoja de Calculo')

    dispatch_id = fields.Many2one('stock.picking', string='Despacho', required=True)

    sale_id = fields.Many2one('sale.order', string='Pedido', required=True)

    date_done = fields.Datetime('Fecha de Entrega')

    state = fields.Selection([('cancel', 'Cancelado'), ('to_delivered', 'Por Despacho'), ('done', 'Realizado')],
                             string='Estado',
                             default='to_delivered')

    image_ids = fields.One2many('ir.attachment', 'res_id')

    dispatch_date = fields.Datetime('Fecha de Despacho')

    company_observations = fields.Text('Observaciones Compañia')

    driver_observations = fields.Text('Observaciones Conductor')

    partner_id = fields.Many2one('res.partner', string="Cliente", related='dispatch_id.partner_id')

    address_to_delivery = fields.Char(related='partner_id.street', string='Direccion de Entrega')

    is_delivered = fields.Boolean('Esta entregado?')

    latitude_delivery = fields.Float('Latitud de Entrega')

    longitude_delivery = fields.Float('Longitude de Entrega')

    product_line_ids = fields.One2many('product.line', 'line_id')

    pallets_quantity = fields.Integer('Lotes', compute="_compute_pallets_quantity")

    kgs_quantity = fields.Float('Kilos', _compute="_compute_kgs_quantity")

    def _compute_pallets_quantity(self):
        for item in self:
            pallet_ids = []
            for line in item.mapped('dispatch_id').mapped('move_line_ids_without_package').mapped('lot_id'):
                if line.id not in pallet_ids:
                    pallet_ids.append(line.id)
            item.pallets_quantity = len(pallet_ids)

    def _compute_kgs_quantity(self):
        for item in self:
            item.kgs_quantity = 0

    def compute_display_name(self):
        for item in self:
            item.display_name = f'Pedido {item.sale_id.name} Cliente {item.partner_id.display_name}'

    def button_cancel(self):
        for item in self:
            item.write({
                'state': 'cancel'
            })

    def button_done(self):
        for item in self:
            item.write({
                'state': 'done',
                'is_delivered': True,
                'date_done': datetime.datetime.now()
            })
            if item.map_id.dispatch_ids.filtered(lambda a: a.state == 'done'):
                item.map_id.write({
                    'state': 'partially_delivered',
                })
            if all(item.map_id.dispatch_ids.mapped('is_delivered')):
                item.map_id.write({
                    'state': 'done',
                    'date_done': datetime.datetime.now()
                })

    def create(self, values):
        dispatch = self.env['route.map.line'].search([('id', '=', values['dispatch_id'])])
        if dispatch:
            raise models.ValidationError('No puede existe mas de una linea de hoja de ruta con el mismo despacho')
        return super(RouteMapLine, self).create(values)
