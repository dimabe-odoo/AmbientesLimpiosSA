from odoo import fields, models, api


class StockPickingAssignLine(models.Model):
    _name = 'assign.line'
    _description = 'Description'

    stock_picking_assign_id = fields.Many2one('stock.picking.assign')

    user_id = fields.Many2one('res.users', string='Usuario',domain=lambda self:[('id','in',self.env.ref('stock.group_stock_user').users.ids)], required=True)

    picking_id = fields.Many2one('stock.picking', string='Picking',
                                 domain=[('state', '!=', 'done'), ('picking_type_id.sequence_code', '=', 'OUT')],
                                 required=True)

    state = fields.Selection(selection=[('done','Hecha')])

    def create(self, values):
        if isinstance(values, list):
            for value in values:
                if 'picking_id' in value.keys() and 'user_id' in value.keys():
                    picking = self.env['stock.picking'].search([('id', '=', value['picking_id'])])
                    picking.write({
                        'user_id': value['user_id']
                    })
        else:
            if 'picking_id' in values.keys() and 'user_id' in values.keys():
                picking = self.env['stock.picking'].search([('id', '=', values['picking_id'])])
                picking.write({
                    'user_id': values['user_id']
                })
        return super(StockPickingAssignLine, self).create(values)
