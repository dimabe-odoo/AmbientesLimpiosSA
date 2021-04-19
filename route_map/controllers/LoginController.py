# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from ..jwt_token import generate_token


class LoginController(http.Controller):

    @http.route('/api/login', type='json', auth='public', cors='*')
    def do_login(self, user, password):
        uid = request.session.authenticate(
            request.env.cr.dbname,
            user,
            password
        )
        if not uid:
            return self.errcode(code=400, message='incorrect login')

        token = generate_token(uid)

        user_object = request.env['res.users'].sudo().search([('id', '=', uid)])


        return {'user': uid,'partner_id': user_object.partner_id.id, 'token': token}
