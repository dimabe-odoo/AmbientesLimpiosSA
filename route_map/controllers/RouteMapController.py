from odoo import http
from odoo.http import request


class RouteMapController(http.Controller):

    @http.route('/api/route_maps', type='json', auth='token', method='GET', cors='*')
    def get_route_maps(self, driver_id):
        maps = request.env['route.map'].sudo().search(
            [('driver_id.id', '=', driver_id), ('state', 'not in', ('done', 'draft'))],
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
        map_object = request.env['route.map'].sudo().search([('id', '=', map_id), ('state', '!=', 'done')])
        lines = []
        if map_object:
            for line in map_object.dispatch_ids:
                products = []
                for product in line.product_line_ids:
                    products.append({
                        'ProductName': product.product_id.name,
                        'Qty': product.qty_to_delivery
                    })
                print(line.sudo().sale_id.id)
                lines.append({
                    'Id': line.id,
                    'Destiny': line.sudo().sale_id.partner_id.name,
                    'Address': line.sudo().address_to_delivery if line.address_to_delivery else '',
                    'LatitudeDestiny': line.sudo().partner_id.partner_latitude,
                    'LongitudeDestiny': line.sudo().partner_id.partner_longitude,
                    'State': line.sudo().state,
                    'Products': products
                })
            res = {
                'Id': map_object.id,
                'Name': map_object.display_name,
                'Sell': map_object.sell if map_object.sell else '',
                'Lines': lines,
                'State': map_object.state
            }
            return {'ok': True, 'result': res}
        else:
            return {'ok': False, 'message': "No existe ningun pedido con este id"}

    @http.route('/api/done', type='json', auth='token', method='GET', cors='*')
    def make_done_line(self, line_id, latitude, longitude, state, to_save_geo=False, observations='', files=None):
        line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
        if line:
            if files and len(files) > 0:
                for file in files:
                    request.env['ir.attachment'].sudo().create({
                        'res_id': line.id,
                        'type': 'binary',
                        'res_model': 'route.map.line',
                        'db_datas': file,
                        'datas': file,
                        'file_size': (len(file) * 6 - file.count('=') * 8) / 8,
                        'name': f"{line.map_id.display_name} Imagen Pedido {line.sale_id.name}",
                        'store_fname': file,
                        'mimetype': 'image/jpeg',
                        'index_content': 'image'
                    })
            if to_save_geo:
                line.partner_id.write({
                    'partner_latitude': latitude,
                    'partner_longitude': longitude
                })
            line.sudo().write({
                'latitude_delivery': latitude,
                'longitude_delivery': longitude,
                'driver_observations': observations
            })
            line.sudo().set_state(state)
            for invoice in line.invoice_ids:
                invoice.write({
                    'file_ids': [(4, f.id) for f in line.image_ids]
                })
            if line.map_id.state == 'done':
                return {'ok': True, 'is_Completed': True, "message": "Hoja Completada"}
        return {'ok': True, "message": "Pedido entregado"}

    @http.route('/api/states', type='json', auth='token', method='GET', cors='*')
    def get_state(self, field_id):
        states = request.env['ir.model.fields.selection'].sudo().search(
            [('field_id', '=', field_id), ('value', '!=', 'to_delivered')])
        res = []
        for state in states:
            res.append({
                'Name': state.name,
                'Value': state.value,
            })
        return res
