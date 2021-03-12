from odoo import models, fields, api
from .helpers import emailValidator

class ResPartner(models.Model):
    _inherit = 'res.partner'
    mail_dte = fields.Char('Email DTE')
    turn_dte = fields.Char('Giro')
    economic_activities_dte = fields.Many2many('custom.economic.activity', string = 'Actividades Económicas')

    @api.onchange('mail_dte')
    def onChangeMailDte(self):
        if emailValidator(self.mail_dte) == False:
            raise models.ValidationError(f'El email {self.mail_dte} no es válido')
        
