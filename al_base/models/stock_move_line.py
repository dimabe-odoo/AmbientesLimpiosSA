from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    supplier_lot = fields.Char('Lote Proveedor')

    is_loteable = fields.Boolean()
    
    def create(self,values):
        for value in values:
            if 'product_id' in value.keys():
                product = self.env['product.product'].search([('id', '=', value['product_id'])])
                value['is_loteable'] = product.tracking == 'lot'
            return super(StockMoveLine, self).create(value)

