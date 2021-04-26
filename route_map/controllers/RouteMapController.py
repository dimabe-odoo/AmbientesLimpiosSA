from odoo import http
from odoo.http import request


class RouteMapController(http.Controller):

    @http.route('/api/route_maps', type='json', auth='token', method='GET', cors='*')
    def get_route_maps(self, driver_id):
        maps = request.env['route.map'].sudo().search([('driver_id.id', '=', driver_id), ('state', '!=', 'done')],
                                                      order='create_date')
        if maps:
            res = []
            for route_map in maps:
                res.append({
                    'Id': route_map.id,
                    'Name': route_map.display_name
                })
            return {'ok': True, 'result': res}
        else:
            return {'ok': False, 'message': 'No tiene hojas activas'}

    @http.route('/api/route_map', type='json', auth='token', method='GET', cors='*')
    def get_route_map(self, map_id):
        map = request.env['route.map'].sudo().search([('id', '=', map_id)])
        lines = []
        if map:
            for line in map.dispatch_ids:
                products = []
                for product in line.product_line_ids:
                    products.append({
                        'ProductName': product.product_id.name,
                        'Qty': product.qty_to_delivery
                    })
                lines.append({
                    'Id': line.id,
                    'Destiny': line.partner_id.name,
                    'Address': line.address_to_delivery,
                    'LatitudeDestiny': line.partner_id.partner_latitude,
                    'LongitudeDestiny': line.partner_id.partner_longitude,
                    'State': line.state,
                    'Products': products
                })
            res = {
                'Id': map.id,
                'Name': map.display_name,
                'Sell': map.sell,
                'Lines': lines,
                'State': map.state
            }
            return {'ok': True, 'result': res}
        else:
            return {'ok': False, 'message': "No existe ningun pedido con este id"}

    @http.route('/api/add_image', type='json', auth='token', cors='*')
    def add_image(self, binary, line_id):
        line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
        request.env['ir.attachment'].sudo().create({
            'res_id': line.id
        })

    @http.route('/api/cancel', type='json', auth='token', cors='*')
    def action_cancel(self, observation, line_id, files):
        line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
        if line:
            for file in files:
                request.env['ir.attachment'].sudo().create({
                    'res_id': line.id,
                    'type': 'binary',
                    'res_model': 'route.map.line',
                    'db_datas': file,
                    'datas':file,
                    'file_size' : (len(file) * 6 - file.count('=') * 8) / 8,
                    'name': f"Prueba {line_id}",
                    'store_fname': file,
                    'mimetype': 'image/jpeg',
                    'index_content':'image'
                })
            line.sudo().write({
                'state': 'cancel',
                'driver_observations': observation
            })
            return {'ok': True, "message": "Pedido devuelto o cancelado"}
        else:
            return {'ok': False, "message": "Error en comunicación"}

    @http.route('/api/done', type='json', auth='token', method='GET', cors='*')
    def make_done_line(self, line_id, latitude, longitude):
        line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
        if line:
            try:
                line.sudo().write({
                    'latitude_delivery': latitude,
                    'longitude_delivery': longitude
                })
                line.sudo().button_done()
            except:
                return {'ok': False, "message": "Error al confirmar"}
        return {'ok': True, "message": "Pedido entregado"}
