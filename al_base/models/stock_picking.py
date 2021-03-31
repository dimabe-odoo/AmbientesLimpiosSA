from odoo import models
from datetime import date
from ..utils.lot_generator import generate_lot


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    def get_last_lot(self):
        now = date.today()
        last_lot = self.env['stock.production.lot'].sudo().search([('name', 'like', '-')])[0]
        if last_lot:
            lot = last_lot.name
            if len(lot.split('-')) == 2:
                return generate_lot(lot)
        return generate_lot()



    def button_validate(self):
        if (self.partner_id and self.partner_id.picking_warn and self.partner_id.picking_warn == 'block') or (self.partner_id.parent_id and self.partner_id.parent_id.picking_warn and self.partner_id.parent_id.picking_warn == 'block'):
            raise models.ValidationError(self.partner_id.picking_warn_msg if self.partner_id.picking_warn_msg else self.partner_id.parent_id.picking_warn_msg)

        for item in self.move_line_nosuggest_ids:
                product = item.product_id
                if not item.lot_id and product.tracking == 'lot':
                    lot = self.get_last_lot()
                    if lot:
                        created_lot = self.env['stock.production.lot'].sudo().create({
                            'name': lot,
                            'product_id': item.product_id.id,
                            'product_qty': item.qty_done
                            'company_id': self.env.user.company_id.id
                        })
                        item.write({
                            'lot_id': created_lot.id
                        })

        return super(StockPicking, self).button_validate()  
