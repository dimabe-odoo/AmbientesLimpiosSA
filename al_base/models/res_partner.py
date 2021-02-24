from odoo import models, api
from ..utils.rut_helper import RutHelper


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        if 'contact' in values.values():
            if 'vat' in values.keys():
                if self.find_partner(values['vat']):
                    raise models.ValidationError(
                        'No se puede crear el contacto ya existe uno con el rut Rut {}'.format(values['vat']))
        return super(ResPartner, self).create(values)

    # @api.model
    # def write(self, values):
    #     currentPartner = self.get_partner(self.id)
    #     existVat = self.find_partner(values['vat'])
    #     if 'child_ids' not in list(values.keys()):
    #         if existVat:
    #             if not existVat.parent_id:
    #                 if currentPartner.vat != values[
    #                     'vat'] and existVat.l10n_latam_identification_type_id.id != currentPartner.l10n_latam_identification_type_id.id:
    #                     raise models.ValidationError(
    #                         'No se puede editar ya que existe un contacto con el rut {}'.format(values['vat']))
    #             else:
    #                 return super(ResPartner, self).write(values)
    #     return super(ResPartner, self).write(values)

    def find_partner(self, rut):
        if rut:
            findPartner = self.env['res.partner'].search(
                [('vat', '=', RutHelper.format_rut(rut)), ('type', '!=', 'contact')])
            if findPartner:
                if len(findPartner) > 1:
                    company = self.env['res.company'].search(
                        [('vat', '=', RutHelper.format_rut(rut)), ('partner_id', 'in', findPartner.mapped('id'))])
                else:
                    company = self.env['res.company'].search(
                        [('vat', '=', RutHelper.format_rut(rut)), ('partner_id', '=', findPartner.id)])
                if company:
                    return None
            return findPartner

    def get_partner(self, id):
        if id:
            return self.env['res.partner'].search([('id', '=', id)])
