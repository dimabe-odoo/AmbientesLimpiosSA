from odoo import fields, models, api

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    def create(self, values):
        for val in values:
            if 'location_id' in val.keys():
                location = self.env['stock.location'].sudo().search([('id', '=', val['location_id'])])
                val['warehouse_id'] = location.get_warehouse().id
        return super(StockWarehouseOrderpoint, self).create(values)
