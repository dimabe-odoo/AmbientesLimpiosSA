from odoo import models

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    def button_validate(self):
        pass