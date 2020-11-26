from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    al_commune_id = fields.Many2one('al.commune', string='Comuna')
    country_id = fields.Many2one('res.country', string='País', default=lambda self: self.env[
        'res.country'].search([('code', '=', 'CL')]))