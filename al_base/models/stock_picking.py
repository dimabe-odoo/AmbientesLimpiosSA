from odoo import models

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    def button_validate(self):
        if self.picking_warn and self.picking_warn == 'block':
            raise models.ValidationError(self.picking_warn_msg)

        return super(StockPicking, self).button_validate()
