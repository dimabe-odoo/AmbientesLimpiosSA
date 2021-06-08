from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    supplier_lot = fields.Char('Lote Proveedor')

    is_loteable = fields.Boolean()

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.is_loteable = self.product_id.tracking == 'lot'

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        self.supplier_lot = self.lot_id.supplier_lot if self.lot_id.supplier_lot else ''

    def create(self, values):
        res = super(StockMoveLine, self).create(values)
        if len(res) > 1:
            for r in res:
                r.verify_stock_move_line()
        else:
            res.verify_stock_move_line()
        return res

    def write(self, values):
        self.verify_stock_move_line()
        return super(StockMoveLine, self).write(values)

    def _action_done(self):
        for item in self:
            item.verify_stock_move_line()
        return super(StockMoveLine, self)._action_done()

    def verify_stock_move_line(self):
        for item in self:
            if item.picking_id:
                if item.picking_id.sale_id:
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
                elif item.picking_id.purchase_id:
                    line = self.env['purchase.order.line'].sudo().search(
                        [('order_id', '=', item.picking_id.purchase_id.id), ('product_id', '=', item.product_id.id)])
                    if line.product_uom_qty < item.qty_done:
                        raise models.UserError(
                            f'No puede validar mas {item.product_id.uom_id.name} de {item.product_id.display_name} de los solicitado en la compra')
