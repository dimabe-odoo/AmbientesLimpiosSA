from odoo import fields, models, api
import hashlib, binascii, os
from ..utils import hash_pasword as password_encoding


class CustomUser(models.Model):
    _name = 'custom.user'

    email = fields.Char('Email', trim=True, required=True)

    name = fields.Char('Nombre', trim=True, required=True)

    password = fields.Char('Contraseña', trim=True, required=True)

    truck_id = fields.Many2one(comodel_name='fleet.vehicle', string='Camion', domain=[('driver_id', '=', None)])

    partner_id = fields.Many2one(comodel_name='res.partner', string='Contacto')

    user_id = fields.Many2one(comodel_name='res.users', string='Usuario')

    has_password = fields.Boolean(compute='compute_password')

    @api.model
    def create(self, values):
        user = self.env['res.users'].sudo().create({
            'login': values['email'],
            'name': values['name'],
            'sel_groups_1_9_10': 9,
            'password': values['password'],
        })
        values['partner_id'] = user.partner_id.id
        values['password'] = password_encoding.create_password(values['password'])
        values['user_id'] = user.id
        if 'truck_id' in values.keys():
            truck = self.env['fleet.vehicle'].sudo().search([('id', '=', values['truck_id'])])
            if truck:
                truck.write({
                    'driver_id': user.partner_id.id
                })
        res = super(CustomUser, self).create(values)
        return res

    def compute_password(self):
        show = False
        if self.password:
            show = True
        self.has_password = show

    def reset_password(self):
        hash_password = password_encoding.hash_password('inicio01')
        self.write({
            'password': hash_password
        })

    def write(self, values):
        if 'truck_id' in values.keys():
            truck = self.env['fleet.vehicle'].sudo().search([('id', '=', values['truck_id'])])
            if truck:
                truck.write({
                    'driver_id': self.partner_id.id
                })
        res = super(CustomUser, self).write(values)
        return res
