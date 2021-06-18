# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from ..jwt_token import generate_token
from ..utils import hash_pasword as password_encoding
from xmlrpc import client


class LoginController(http.Controller):

    @http.route('/api/login', type='json', auth='none', cors='*')
    def do_login(self, user, password):
        url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        db_name = request._cr.dbname
        common = client.ServerProxy(f'{url}/xmlrpc/2/common'.format(url))
        models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.authenticate(db_name, user, password, {})
        user = models.execute_kw(db_name, uid, password,
                                 'res.users', 'search_read',
                                 [[['id', '=', uid]]],
                                 {'fields': ['name', 'partner_id', 'login'], 'limit': 1})[0]
        user['token'] = generate_token(uid)
        return user

    @http.route('/api/reset_password', type='json', auth='public', cors='*')
    def reset_password(self, email):
        user_id = request.env['custom.user'].sudo().search([('email', '=', email)])
        if user_id:
            uid = request.session.authenticate(
                request.env.cr.dbname,
                user_id.email,
                password_encoding.decrypt_password(user_id.password.encode())
            )
            request.env['res.users'].sudo().search([('id', '=', uid)]).action_reset_password()
            return {'ok': True, 'message': "Correo de restablecimiento de contraseña enviado"}
        else:
            return {'ok': False, 'message': "Usuario no Encontrado"}
