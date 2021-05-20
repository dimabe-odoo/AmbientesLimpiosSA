# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from ..jwt_token import generate_token
from ..utils import hash_pasword as password_encoding


class LoginController(http.Controller):

    @http.route('/api/login', type='json', auth='public', cors='*')
    def do_login(self, user, password):
        user_id = request.env['custom.user'].sudo().search([('email', '=', user)])
        uid = 0
        if user_id:
            if password == password_encoding.decrypt_password(user_id.password.encode()).decode():
                uid = request.session.authenticate(
                    request.env.cr.dbname,
                    user_id.email,
                    password_encoding.decrypt_password(user_id.password.encode())
                )
        else:
            uid = request.session.authenticate(
                request.env.cr.dbname,
                user,
                password
            )
        if not uid:
            return self.errcode(code=400, message='incorrect login')

        token = generate_token(uid)

        user_object = request.env['res.users'].sudo().search([('id', '=', uid)])

        return {'user': uid, 'partner_id': user_object.partner_id.id, 'name': user_object.name, 'token': token,
                'email': user_object.login}
