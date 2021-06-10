from odoo import fields, models, api


class QualityAlert(models.Model):
    _inherit = 'quality.alert'

    @api.onchange('picking_id')
    def onchange_picking(self):
        if self.picking_id.purchase_id:
            res = {
                'domain': {
                    'product_tmpl_id': [('id', 'in',
                                         self.picking_id.purchase_id.order_line.mapped('product_id').mapped(
                                             'product_tmpl_id').mapped('id'))]
                }
            }
            return res
