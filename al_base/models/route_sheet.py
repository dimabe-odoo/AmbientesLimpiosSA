from odoo import fields, models
from odoo.models import Model
from odoo.fields import Many2one, One2many, Selection,Char,Date,Datetime


class RouteSheet(Model):
    _name = 'route.sheet'

    driver_id = Many2one('custom.driver', string='Conductor')

    truck_id = Many2one('custom.truck', string='Camion')

    picking_id = Many2one('stock.picking', 'Despacho', domain=[('sheet_id', '=', None), ('state', '=', 'done')])

    dispatch_ids = One2many('stock.picking', 'sheet_id', string="Despacho")

    sell = Char('Sello')

    state = Selection([('draft','Borrador'),('incoming','Despachado'),('done','Entregado')],string="Estado",readonly=True)

    dispatch_date = Datetime('Fecha de Despacho')

    date_done = Datetime('Fecha Realizado')

    def add_picking(self):
        self.picking_id.write({
            'sheet_id': self.id
        })
        self.write({
            'picking_id': None
        })


    def generate_route_sheet(self):
        return self.env.ref('action_report_route_sheet') \
            .report_action(self)
