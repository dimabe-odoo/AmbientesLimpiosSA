from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    file_ids = fields.Many2many('ir.attachment', compute='compute_files')

    def compute_files(self):
        route_map_line = self.env['route.map.line'].search([])
        for line in route_map_line:
            if self in line.mapped('invoice_ids'):
                self.files = line.image_ids
                break
