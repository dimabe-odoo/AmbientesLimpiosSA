from odoo import fields, models, api, tools, SUPERUSER_ID
from ..utils import hash_pasword as password_encoding


class ResUser(models.Model):
    _inherit = 'res.users'

    def write(self, values):
        custom_user_id = self.env['custom.user'].search([('user_id', '=', self.id)])
        if custom_user_id and 'password' in values.keys():
            custom_user_id.write({
                'password': password_encoding.create_password(values['password']).decode()
            })
        res = super(ResUser, self).write(values)
        return res

    @api.model
    @tools.ormcache('self._uid', 'group_ext_id')
    def _has_group(self, group_ext_id):
        if not self._uid:
            module, ext_id = group_ext_id.split('.')
            self._cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid IN
                                        (SELECT res_id FROM ir_model_data WHERE module=%s AND name=%s)""",
                             (SUPERUSER_ID, module, ext_id))
            return bool(self._cr.fetchone())
        else:
            return super(ResUser, self)._has_group(group_ext_id)
