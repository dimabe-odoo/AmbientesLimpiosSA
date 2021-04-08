from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    supplier_lot = fields.Char('Lote Proveedor')

    is_loteable = fields.Boolean()
    
    def create(self,values):
        if 'product_id' in values.keys():
            product = self.env['product.product'].search([('id','=',values['product_id'])])
            values['is_loteable'] = product.tracking == 'lot'
        return super(StockMoveLine, self).create(values)