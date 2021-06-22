from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'ir.attachment'

    invoice_id = fields.Many2one('account.move')
