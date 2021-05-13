from odoo import fields, models


class CustomCollectionGroup(models.Model):
    _name = 'custom.collection.group'

    name = fields.Char('Nombre Grupo')

    user_ids = fields.Many2many('res.users', string='Usuarios')

    def write(self, values):
        res = super(CustomCollectionGroup, self).write(values)
        group_id = self.env['res.groups'].search([('id','=', self.env.ref('al_base.group_order_confirmation').id)])

        if 'user_ids' in values.keys():
            if 2 not in values['user_ids'][0][2]:
                values['user_ids'][0][2].append(2)

            group_id.write({
                'users': values['user_ids']
            })
        return res
