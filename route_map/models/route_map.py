from odoo import fields, models, api
from odoo.models import Model
from datetime import datetime
from xmlrpc import client


class RouteMap(Model):
    _name = 'route.map'
    _rec_name = 'display_name'

    display_name = fields.Char('Nombre a mostrar')

    type_of_map = fields.Selection([('client', 'Cliente'), ('other', 'Otro')])

    truck_id = fields.Many2one('fleet.vehicle', string='Camion', required=True)

    driver_id = fields.Many2one('res.partner', string='Conductor', related='truck_id.driver_id')

    sale_id = fields.Many2one('sale.order', 'Pedido',
                              domain=[('state', 'in', ['sale', 'done']), ('invoice_ids', '!=', False),
                                      ('invoice_publish_ids', '!=', False)])

    picking_other_id = fields.Many2one('stock.picking',
                                       domain=[('state', '=', 'done'), ('map_id', '=', False),
                                               ('picking_type_id.sequence_code', 'in', ['IN', 'OUT'])
                                               ])

    dispatch_ids = fields.One2many('route.map.line', 'map_id', string="Despacho")

    sell = fields.Char('Sello')

    state = fields.Selection(
        [('draft', 'Borrador'), ('incoming', 'Despachado'), ('partially_delivered', 'Parcialmente Realizado'),
         ('done', 'Realizado')], default='draft', string="Estado", readonly=True)

    dispatch_date = fields.Datetime('Fecha de Despacho')

    date_done = fields.Datetime('Fecha Realizado')

    add_more = fields.Boolean('Puede agregar mas?')

    observations = fields.Text('Observaciones')

    packages_sum = fields.Integer('Total Bultos', compute="_packages_sum")

    kgs_sum = fields.Integer('Total Kgs', compute="_kgs_sum")

    pallets_sum = fields.Integer('Total Pallets', compute="_pallets_sum")

    invoices_name = fields.Char('Facturas', compute='compute_invoices_name')

    route_value = fields.Float('Valor:')

    has_regional_value = fields.Boolean('Tiene Valor Regional')

    total_regional_value = fields.Float('Valor Regional')

    change_from_line = fields.Boolean('Cambio datos desde la linea')

    sale_ids = fields.Many2many('sale.order', compute='compute_sale_ids')

    def compute_sale_ids(self):
        for item in self:
            item.sale_ids = self.dispatch_ids.mapped('sale_id')

    def action_dispatch(self):
        for item in self:
            item.write({
                'state': 'incoming'
            })

    @api.onchange('truck_id')
    def onchange_truck_id(self):
        for item in self:
            item.route_value = item.truck_id.transport_value

    def compute_invoices_name(self):
        for item in self:
            item.invoices_name = ','.join(item.dispatch_ids.mapped('invoices_name'))

    def add_picking(self):
        if self.type_of_map == 'client':
            for picking in self.sale_id.picking_ids.filtered(
                    lambda x: x.picking_type_id.sequence_code != 'IN' and x.state == 'done'):
                route_map_line = self.env['route.map.line'].search(
                    [('map_id', '!=', self.id), ('dispatch_id.id', '=', picking.id)])
                if route_map_line:
                    continue
                line = self.env['route.map.line'].sudo().create({
                    'map_id': self.id,
                    'dispatch_id': picking.id,
                    'sale_id': self.sale_id.id,
                    'line_value': self.route_value if len(self.dispatch_ids) == 0 else self.route_value / len(
                        self.dispatch_ids)
                })
                for product in picking.move_line_ids_without_package:
                    self.env['product.line'].sudo().create({
                        'line_id': line.id,
                        'product_id': product.product_id.id,
                        'qty_to_delivery': product.qty_done
                    })
                picking.sudo().write({
                    'map_id': self.id
                })
            if len(self.dispatch_ids) > 1:
                for line in self.dispatch_ids:
                    line.write({
                        'line_value': self.route_value / len(self.dispatch_ids)
                    })
            self.write({
                'sale_id': None
            })
        else:
            line = self.env['route.map.line'].sudo().create({
                'map_id': self.id,
                'dispatch_id': self.picking_other_id.id,
                'line_value': self.route_value if len(self.dispatch_ids) == 0 else self.route_value / len(
                    self.dispatch_ids)
            })
            if len(self.dispatch_ids) > 1:
                for line in self.dispatch_ids:
                    line.write({
                        'line_value': self.route_value / len(self.dispatch_ids)
                    })
            for product in self.picking_id.move_line_ids_without_package:
                self.env['product.line'].sudo().create({
                    'line_id': line.id,
                    'product_id': product.product_id.id,
                    'qty_to_delivery': product.qty_done
                })
            self.picking_other_id.sudo().write({
                'map_id': self.id,
            })
            self.write({
                'picking_other_id': None
            })

    @api.model
    def create(self, values):
        values['display_name'] = self.env['ir.sequence'].next_by_code('route.map.seq')
        return super(RouteMap, self).create(values)

    def action_dispatch(self):
        self.dispatch_ids.write({
            'dispatch_date': datetime.now()
        })
        self.write({
            'state': 'incoming',
            'dispatch_date': datetime.now()
        })

    def _packages_sum(self):
        for item in self:
            packages_sum = 0
            for line in item.dispatch_ids.product_line_ids:
                packages_sum += line.qty_to_delivery
            item.packages_sum = packages_sum

    def _kgs_sum(self):
        for item in self:
            kgs_sum = 0
            for line in item.dispatch_ids:
                kgs_sum += line.kgs_quantity
            item.kgs_sum = kgs_sum

    def _pallets_sum(self):
        for item in self:
            pallets_sum = 0
            for line in item.dispatch_ids:
                pallets_sum += line.pallet_qty
            item.pallets_sum = pallets_sum
