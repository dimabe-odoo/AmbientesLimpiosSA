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

    def verify_stock_move_line(self):
        if self.picking_id:
            if self.picking_id.sale_id:
                line = self.env['sale.order'].sudo().search(
                    [('order_id', '=', self.picking_id.order_id.id), ('product_id', '=', self.product_id.id)])
                if line.qty_delivered == 0:
                    if self.product_uom_qty < self.qty_done:
                        raise models.UserError(
                            f'No puede validar mas {self.product_id.uom_id.name} de {self.product_id.display_name} de los solicitado en la venta')
