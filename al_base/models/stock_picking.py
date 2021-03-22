from odoo import models

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    def button_validate(self):
        if self.partner_id and self.partner_id.picking_warn and self.partner_id.picking_warn == 'block':
            raise models.ValidationError(self.partner_id.picking_warn_msg)

        return super(StockPicking, self).button_validate()
