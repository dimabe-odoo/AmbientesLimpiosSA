from odoo import fields, models, api


class StockPickingAssign(models.Model):
    _name = 'stock.picking.assign'

    name = fields.Char('Nombre', default=lambda self: self.env['ir.sequence'].next_by_code('stock.assign.code'))

    assign_line_ids = fields.One2many('assign.line', 'stock_picking_assign_id', string='Asignaciones')
