from odoo import fields, models
from odoo.models import Model
from datetime import datetime


class RouteMap(Model):
    _name = 'route.map'
    _rec_name = 'display_name'

    display_name = fields.Char('Nombre a mostrar', compute='compute_display_name')

    truck_id = fields.Many2one('fleet.vehicle', string='Camion', required=True)

    driver_id = fields.Many2one('res.partner', string='Conductor', related='truck_id.driver_id')

    picking_id = fields.Many2one('stock.picking', 'Despacho')

    dispatch_ids = fields.One2many('route.map.line', 'map_id', string="Despacho")

    sell = fields.Char('Sello')

    state = fields.Selection(
        [('draft', 'Borrador'), ('incoming', 'Despachado'), ('partially_delivered', 'Parcialmente Entregado'),
         ('done', 'Entregado')], default='draft', string="Estado", readonly=True)

    dispatch_date = fields.Datetime('Fecha de Despacho')

    date_done = fields.Datetime('Fecha Realizado')

    add_more = fields.Boolean('Puede agregar mas?')

    observations = fields.Text('Observaciones')

    def compute_display_name(self):
        for item in self:
            item.display_name = f'{item.driver_id.name} {item.truck_id.license_plate} '

    def add_picking(self):
        line = self.env['route.map.line'].sudo().create({
            'map_id': self.id,
            'dispatch_id': self.picking_id.id,
            'sale_id': self.picking_id.sale_id.id,
        })
        for product in self.picking_id.move_line_ids_without_package:
            self.env['product.line'].sudo().create({
                'line_id': line.id,
                'product_id': product.product_id.id,
                'qty_to_delivery': product.qty_done
            })
        self.picking_id.sudo().write({
            'map_id': self.id
        })
        self.write({
            'picking_id': None
        })

    def action_dispatch(self):
        self.dispatch_ids.write({
            'dispatch_date': datetime.now()
        })
        self.write({
            'state': 'incoming',
            'dispatch_date': datetime.now()
        })
