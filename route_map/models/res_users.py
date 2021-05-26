from odoo import fields, models, api
from ..utils import hash_pasword as password_encoding


class ResUser(models.Model):
    _inherit = 'res.users'

    @api.model
    def write(self, values):
        custom_user_id = self.env['custom.user'].search([('user_id', '=', self.id)])
        if custom_user_id and 'password' in values.keys():
            custom_user_id.write({
                'password': password_encoding.create_password(values['password']).decode()
            })
        res = super(ResUser, self).write(values)
        return res
