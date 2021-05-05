from odoo import models, fields ,api
class ResPartner(models.Model):
    _inherit = 'res.partner'

    comercionet_box = fields.Char('Casilla Comercionet')

    @api.model
    def create(self,values):
        if 'comercionet_box' in values.keys():
            values['comercionet_box'] = values['comercionet_box'].strip()
        return super(ResPartner, self).create(values)

    @api.model
    def write(self, values):
        if 'comercionet_box' in values.keys():
            values['comercionet_box'] = values['comercionet_box'].strip()
        return super(ResPartner, self).write(values)