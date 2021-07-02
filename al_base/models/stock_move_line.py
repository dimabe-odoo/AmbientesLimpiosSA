from odoo import models, fields, api
from py_linq import Enumerable


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    supplier_lot = fields.Char('Lote Proveedor')

    is_loteable = fields.Boolean()

    stock_product_qty = fields.Float('Stock Disponible', compute="_compute_stock_product_qty", digits=[16, 3])

    product_quant_ids = fields.Many2many('stock.quant', compute='_compute_stock_product_qty')

    product_lot_ids = fields.Many2many('stock.production.lot')

    @api.onchange('product_id', 'location_id', 'lot_id')
    def onchange_product_stock(self):
        res = {
            'domain': {
                'lot_id': [('id', 'in', self.product_id.stock_quant_ids.filtered(
                    lambda x: x.location_id.id == self.location_id.id).mapped('lot_id').ids)]
            }
        }
        return res

    @api.onchange('location_dest_id')
    def onchange_location_dest_id(self):
        for item in self:
            if item.picking_id.picking_type_id == 'INT':
                if item.location_id.id == item.location_dest_id.id:
                    raise models.ValidationError('No puede seleccionar la misma ubicacion para una transferencia')

    @api.onchange('product_id', 'lot_id')
    def _compute_stock_product_qty(self):
        for item in self:
            if item.lot_id.product_id != item.product_id:
                item.lot_id = None
            if item.product_id.tracking != 'lot':
                quant = Enumerable(item.product_id.stock_quant_ids).where(
                    lambda x: x.location_id.id == item.location_id.id)
                item.product_quant_ids = item.product_id.stock_quant_ids.filtered(
                    lambda x: x.location_id.id == item.location_id.id)
                test = quant.sum(lambda x: x.quantity)
                print(test)
                item.stock_product_qty = quant.sum(lambda x: x.quantity)
            else:
                quant = item.product_id.stock_quant_ids.filtered(lambda x: x.location_id.id == self.location_id.id)
                if item.lot_id:
                    quant = quant.filtered(lambda x: x.lot_id.id == item.lot_id.id)
                item.stock_product_qty = sum(quant.mapped('quantity'))
                item.product_quant_ids = quant

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        self.supplier_lot = self.lot_id.supplier_lot if self.lot_id.supplier_lot else ''

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.is_loteable = self.product_id.tracking == 'lot'

    @api.onchange('location_id')
    def onchange_location(self):
        self.show_lot_with_stock()

    def show_lot_with_stock(self):
        quants = self.env['stock.quant'].search(
            [('product_id', '=', self.product_id.id), ('location_id', '=', self.location_id.id), ('quantity', '>', 0)])
        return {
            'domain': {
                'lot_id': [
                    ('id', 'in', quants.lot_id.ids)
                ]
            }
        }

    @api.model
    def create(self, values):
        res = super(StockMoveLine, self).create(values)
        if len(res) > 1:
            for r in res:
                r.verify_stock_move_line()
        else:
            res.verify_stock_move_line()
        res.product_lot_ids = res.product_id.stock_quant_ids.filtered(
            lambda x: x.location_id.id == res.location_id.id).mapped('lot_id')
        return res

    def write(self, values):
        res = super(StockMoveLine, self).write(values)
        self.verify_stock_move_line()
        return res

    def _action_done(self):
        for item in self:
            item.verify_stock_move_line()
        return super(StockMoveLine, self)._action_done()

    def verify_stock_move_line(self):
        for item in self:
            if item.picking_id and item.qty_done and item.qty_done > 0:
                if item.picking_id.sale_id and item.picking_id.picking_type_id.sequence_code == 'OUT':
                    line = item.env['sale.order.line'].sudo().search(
                        [('order_id', '=', item.picking_id.sale_id.id), ('product_id', '=', item.product_id.id)])
                    if line.qty_delivered == 0:
                        if line.product_uom_qty < item.qty_done:
                            raise models.UserError(
                                f'No puede validar mas {item.product_id.uom_id.name} de {item.product_id.display_name} de los solicitado en la venta')
                    elif line.qty_delivered != 0:
                        qty_remaining = line.product_uom_qty - line.qty_delivered
                        if qty_remaining < item.qty_done:
                            raise models.UserError(
                                f'No puede validar mas {item.product_id.uom_id.name} de {item.product_id.display_name} de la cantidad restante a entregar de la venta')
                elif item.picking_id.purchase_id and item.picking_id.picking_type_id.sequence_code == 'IN' and item.qty_done and item.qty_done > 0:
                    lines = self.env['purchase.order.line'].sudo().search(
                        [('order_id', '=', item.picking_id.purchase_id.id), ('product_id', '=', item.product_id.id)])
                    if isinstance(lines, list):
                        for line in lines:
                            if self.env.user.company_id.tolerance_percentage and self.env.user.company_id.tolerance_percentage > 0:
                                tolerance = self.env.user.company_id.tolerance_percentage
                                qty = (line.product_uom_qty * tolerance) / 100 + line.product_uom_qty
                                if qty < item.qty_done:
                                    raise models.UserError(
                                        f'No puede validar mas {item.product_id.uom_id.name} de {item.product_id.display_name} de los solicitado en la compra')
                            elif line.product_uom_qty < item.qty_done:
                                raise models.UserError(
                                    f'No puede validar mas {item.product_id.uom_id.name} de {item.product_id.display_name} de los solicitado en la compra')
                    else:
                        if self.env.user.company_id.tolerance_percentage and self.env.user.company_id.tolerance_percentage > 0:
                            tolerance = self.env.user.company_id.tolerance_percentage
                            qty = (lines.product_uom_qty * tolerance) / 100 + lines.product_uom_qty
                            if qty < item.qty_done:
                                raise models.UserError(
                                    f'No puede validar mas {item.product_id.uom_id.name} de {item.product_id.display_name} de los solicitado en la compra')
                        elif lines.product_uom_qty < item.qty_done:
                            raise models.UserError(
                                f'No puede validar mas {item.product_id.uom_id.name} de {item.product_id.display_name} de los solicitado en la compra')
