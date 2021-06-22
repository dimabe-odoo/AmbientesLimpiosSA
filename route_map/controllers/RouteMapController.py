from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.tools import date_utils
from ..utils.process_line import make_done
import json
from py_linq import Enumerable
from xmlrpc import client


class RouteMapController(http.Controller):

    @http.route('/api/route_maps', type='json', auth='token', method='GET', cors='*')
    def get_route_maps(self, driver_id):
        url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        db_name = request._cr.dbname
        models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        record = models.execute_kw(db_name, 2, 'dimabe21',
                                   'route.map', 'search_read',
                                   [[['driver_id', '=', driver_id], ('state', '!=', 'done')]],
                                   {'fields': ['display_name', 'type_of_map'], 'limit': 5})
        return record

    @http.route('/api/route_map', type='json', auth='token', method='GET', cors='*')
    def get_route_map(self, map_id):
        url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        db_name = request._cr.dbname
        models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        ids = models.execute_kw(db_name, 2, 'dimabe21',
                                'route.map', 'search',
                                [[['id', '=', map_id]]])
        record = models.execute_kw(db_name, 2, 'dimabe21',
                                   'route.map', 'read', [ids])[0]
        index = 0
        for dispatch in record['dispatch_ids']:
            dispatch_read = models.execute_kw(db_name, 2, 'dimabe21',
                                              'route.map.line', 'search_read',
                                              [[['id', '=', dispatch]]],
                                              {'fields': ['partner_latitude', 'partner_longitude', 'partner_id',
                                                          'state', 'address_to_delivery','picking_code'], 'limit': 5})
            record['dispatch_ids'][index] = dispatch_read
            index += 1
        return record

    @http.route('/api/done', type='json', auth='token', method='GET', cors='*')
    def make_done_line(self, line_id, latitude, longitude, state, observations='', files=None,
                       ):
        line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
        is_done = False
        if line:
            if files and len(files) > 0:
                for file in files:
                    data = {
                        'res_id': line.id,
                        'type': 'binary',
                        'res_model': 'route.map.line',
                        'db_datas': file,
                        'datas': file,
                        'file_size': (len(file) * 6 - file.count('=') * 8) / 8,
                        'name': f"{line.map_id.display_name} Imagen Pedido {line.sale_id.name} 12",
                        'store_fname': file,
                        'mimetype': 'image/jpeg'
                    }
                    if line.invoice_ids:
                        data['invoice_id'] = line.invoice_ids[0].id
                    make_done(data=data, state=state, latitude=latitude, longitude=longitude, observations=observations)
                    if Enumerable(line.map_id.dispatch_ids).all(lambda x: x.state != 'to_delivered'):
                        url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        db_name = request._cr.dbname
                        models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
                        models.execute_kw(db_name, 2, 'dimabe21', 'route.map', 'write', [[line.map_id.id], {
                            'state': 'done',
                        }])
                        is_done = True
            if is_done:
                return {'ok': True, 'is_Completed': True, "message": "Hoja Completada"}
        return {'ok': True, "message": "Pedido entregado"}

    @http.route('/api/states', type='json', auth='token', method='GET', cors='*')
    def get_state(self):
        url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        db_name = request._cr.dbname
        models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        state = models.execute_kw(db_name, 2, 'dimabe21', 'ir.model.fields.selection', 'search_read', [
            [['field_id.model_id.name', '=', 'route.map.line'], ['value', '!=', 'to_delivered']]],
                                  {'fields': ['name', 'value']})
        return state
