from odoo import fields, models, api

class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.model
    def create(self, values):
        if isinstance(values,list):
            for val in values:
                if 'location_id' in val.keys():
                    location = self.env['stock.location'].sudo().search([('id', '=', val['location_id'])])
                    val['warehouse_id'] = location.get_warehouse().id
        else:
            if 'location_id' in values.keys():
                location = self.env['stock.location'].sudo().search([('id', '=', values['location_id'])])
                values['warehouse_id'] = location.get_warehouse().id
        return super(StockWarehouseOrderpoint, self).create(values)
