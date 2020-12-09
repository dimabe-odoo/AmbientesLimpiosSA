from odoo import models, api
from ..utils.rut_helper import RutHelper

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        if self.find_partner(values['vat']):
            raise models.ValidationError('Ya existe un contacto con el Rut')
        return super(ResPartner, self).create(values)

    def write(self, values):
        exist = self.find_partner(values['vat'])
        if exist and exist.id != values['id']:
            raise models.ValidationError('Ya existe un contacto con el Rut')
        return super(ResPartner, self).write(values)

    def find_partner(self, rut):
        return self.env['res.partner'].search([('vat','=',RutHelper.format_rut(rut))])
