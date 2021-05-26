from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    file_ids = fields.Many2many('ir.attachment')

    show_files = fields.Boolean('Mostrar Archivos',compute='compute_show_files')

    def compute_show_files(self):
        self.show_files = self.file_ids and len(self.file_ids) > 0



