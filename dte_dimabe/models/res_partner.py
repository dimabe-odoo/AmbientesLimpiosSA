from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    mail_dte = fields.Char('Email DTE')
    turn_dte = fields.Char('Giro')
    economic_activities_dte = fields.Many2many('custom.economic.activity', string = 'Actividades Económicas')