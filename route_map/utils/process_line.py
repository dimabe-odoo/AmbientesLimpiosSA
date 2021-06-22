from xmlrpc import client
from odoo import http
from odoo.http import request


def make_done(data, state, latitude, longitude, observations):
    url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    db_name = request._cr.dbname
    models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    user = request.env['ir.config_parameter'].sudo().get_param('user_admin')
    password = request.env['ir.config_parameter'].sudo().search([('key','=','user_admin_pass')]).password
    common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db_name, user, password, {})

    models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    models.execute_kw(db_name, uid, password, 'ir.attachment', 'create', [data])
    models.execute_kw(db_name, uid, password, 'route.map.line', 'write', [[data['res_id']], {
        'state': state,
        'latitude_delivery': latitude,
        'longitude_delivery': longitude,
        'driver_observations': observations
    }])
