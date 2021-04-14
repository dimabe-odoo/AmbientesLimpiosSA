from odoo import fields, models, api
from ..utils.lot_generator import generate_lot_prd
from datetime import date


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def get_last_lot(self):
        now = date.today()
        last_lot = self.env['stock.production.lot'].sudo().search([('is_prd_lot', '=', True)], order='id desc', limit=1)
        if last_lot:
            lot = last_lot.name
            return generate_lot_prd(lot)
        return generate_lot_prd()

    def action_generate_serial(self):
        self.ensure_one()
        name = self.get_last_lot()
        self.lot_producing_id = self.env['stock.production.lot'].create({
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'is_prd_lot': True,
            'name': name
        })
        if self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id).move_line_ids:
            self.move_finished_ids.filtered(
                lambda m: m.product_id == self.product_id).move_line_ids.lot_id = self.lot_producing_id
        if self.product_id.tracking == 'serial':
            self._set_qty_producing()