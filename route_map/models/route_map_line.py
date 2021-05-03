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

    state = fields.Selection(
        [('to_delivered', 'Por Despachar'), ('ok', 'Entrega Ok'), ('parcial', 'Entrega Parcial'),
         ('rejected', 'Rechazo Total Cliente'),
         ('homeless', 'Sin Moradores'), ('after hour', 'Fuera de Horario')],
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

    invoice_ids = fields.Many2many('account.move', compute='compute_invoice_ids')

    invoices_name = fields.Char('Factura', compute='compute_invoice_name')

    def _compute_pallets_quantity(self):
        for item in self:
            pallet_ids = []
            for line in item.mapped('dispatch_id').mapped('move_line_ids_without_package').mapped('lot_id'):
                if line.id not in pallet_ids:
                    pallet_ids.append(line.id)
            item.pallets_quantity = len(pallet_ids)

    def compute_invoice_ids(self):
        for item in self:
            item.invoice_ids = item.sale_id.invoice_ids

    def compute_invoice_name(self):
        for item in self:
            item.invoices_name = ','.join(item.invoice_ids.mapped('name'))

    def _compute_kgs_quantity(self):
        for item in self:
            item.kgs_quantity = 0

    def compute_display_name(self):
        for item in self:
            item.display_name = f'Pedido {item.sale_id.name} Cliente {item.partner_id.display_name} Factura {",".join(item.invoice_ids.mapped("name"))}'

    def button_cancel(self):
        for item in self:
            item.write({
                'state': 'cancel'
            })
            if self.verify_all_line(item.map_id.dispatch_ids):
                item.map_id.write({
                    'state': 'done',
                    'date_done': datetime.datetime.now()
                })

    def button_done(self):
        for item in self:
            if item.state == 'cancel':
                raise models.ValidationError('No se puede entregar un pedido ya cancelado')
            item.write({
                'state': 'done',
                'is_delivered': True,
                'date_done': datetime.datetime.now()
            })
            if item.map_id.dispatch_ids.filtered(lambda a: a.state == 'done'):
                item.map_id.write({
                    'state': 'partially_delivered',
                })
            if self.verify_all_line(item.map_id.dispatch_ids):
                item.map_id.write({
                    'state': 'done',
                    'date_done': datetime.datetime.now()
                })

    def set_state(self,state):
        for item in self:
            if item.state == state:
                raise models.ValidationError('No se puede entregar un pedido ya cancelado')
            item.write({
                'state': state,
                'is_delivered': True,
                'date_done': datetime.datetime.now()
            })
            if item.map_id.dispatch_ids.filtered(lambda a: a.state == 'done'):
                item.map_id.write({
                    'state': 'partially_delivered',
                })
            if self.verify_all_line(item.map_id.dispatch_ids):
                item.map_id.write({
                    'state': 'done',
                    'date_done': datetime.datetime.now()
                })

    def verify_all_line(self, dispatch_ids):
        for item in dispatch_ids:
            if item.state == 'to_delivered':
                return False
        return True

    def create(self, values):
        dispatch = self.env['route.map.line'].search([('id', '=', values['dispatch_id']), ('state', '!=', 'cancel')])
        if dispatch:
            raise models.ValidationError('No puede existe mas de una linea de hoja de ruta con el mismo despacho')
        return super(RouteMapLine, self).create(values)
