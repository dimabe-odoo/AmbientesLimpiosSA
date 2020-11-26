from odoo import models, fields, api

class AlCommune(models.Model):
    _name = 'al.commune'
    state_id = fields.Many2one('res.country.state', string='Región')
    name = fields.Char(string='Comuna')
