from odoo import fields, models,api
from odoo.models import Model
from datetime import datetime


class RouteMap(Model):
    _name = 'route.map'
    _rec_name = 'display_name'

    display_name = fields.Char('Nombre a mostrar')

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

    packages_sum = fields.Integer('Total Bultos', compute="_packages_sum")

    kgs_sum = fields.Integer('Total Kgs', compute="_kgs_sum")

    pallets_sum = fields.Integer('Total Pallets', compute="_pallets_sum")


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

    @api.model
    def create(self,values):
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
                pallets_sum += line.pallets_quantity
            item.pallets_sum = pallets_sum
