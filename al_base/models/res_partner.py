from odoo import models, api
from ..utils.rut_helper import RutHelper

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        if self.find_partner(values['vat']):
            raise models.ValidationError('No se puede crear el contacto ya existe uno con el rut Rut {}'.format(values['vat']))
        return super(ResPartner, self).create(values)

    def write(self, values):
        exist = self.find_partner(values['vat'])
        if not exist:
            raise models.ValidationError('No se puede editar el contacto')
        return super(ResPartner, self).write(values)

    def find_partner(self, rut):
        return self.env['res.partner'].search([('vat','=',RutHelper.format_rut(rut))])
