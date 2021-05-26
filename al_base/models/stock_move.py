from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_record_components(self):
        production = self.move_orig_ids.production_id[-1:]
        if not production.lot_producing_id:
            production.action_generate_serial()
        return super(StockMove, self)._action_record_components()