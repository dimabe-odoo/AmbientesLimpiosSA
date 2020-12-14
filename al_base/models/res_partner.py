from odoo import models, api
from ..utils.rut_helper import RutHelper


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        if 'vat' in values.keys():
            if self.find_partner(values['vat']):
                raise models.ValidationError(
                    'No se puede crear el contacto ya existe uno con el rut Rut {}'.format(values['vat']))

        return super(ResPartner, self).create(values)

    @api.model
    def write(self, values):
        exist = self.find_partner(values['vat'])
        raise models.ValidationError('Exist: {}  values actual: {}'.format(exist,values))

        if exist:
            if exist.vat != values['vat'] and exist.id != values['id']:
                raise models.ValidationError(
                    'No se puede editar ya que existe un contacto con el rut {}'.format(values['vat']))
        return super(ResPartner, self).write(values)

    def find_partner(self, rut):
        if rut:
            findP = self.env['res.partner'].search([('vat', '=', RutHelper.format_rut(rut))])
            if findP:
                if len(findP) > 1:
                    company = self.env['res.company'].search([('vat','=',RutHelper.format_rut(rut)),('partner_id','in',findP.mapped('id'))])
                else:
                    company = self.env['res.company'].search([('vat','=',RutHelper.format_rut(rut)),('partner_id','=',findP.id)])
                if company:
                    return None
            return self.env['res.partner'].search([('vat', '=', RutHelper.format_rut(rut))])
