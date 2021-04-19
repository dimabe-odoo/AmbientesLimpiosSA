import datetime

from odoo import models, fields, api


class RouteMapLine(models.Model):
    _name = 'route.map.line'

    map_id = fields.Many2one('route.map', string='Hoja de Calculo')

    dispatch_id = fields.Many2one('stock.picking', string='Despacho', required=True)

    sale_id = fields.Many2one('sale.order', string='Pedido', required=True)

    date_done = fields.Datetime('Fecha de Entrega')

    state = fields.Selection([('to_delivered', 'Por Despacho'), ('done', 'Realizado')], string='Estado',
                             default='to_delivered')

    partner_id = fields.Many2one('res.partner', string="Cliente", related='dispatch_id.partner_id')

    address_to_delivery = fields.Char(related='partner_id.street', string='Direccion de Entrega')

    is_delivered = fields.Boolean('Esta entregado?')

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
                    'state': 'done'
                })

    def create(self, values):
        dispatch = self.env['route.map.line'].search([('id', '=', values['dispatch_id'])])
        if dispatch:
            raise models.ValidationError('No puede existe mas de una linea de hoja de ruta con el mismo despacho')
        return super(RouteMapLine, self).create(values)
