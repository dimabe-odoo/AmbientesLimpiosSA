from odoo import http
from odoo.http import request


class RouteMapController(http.Controller):

    @http.route('/api/route_map', type='json', auth='token', method='GET', cors='*')
    def get_route_map(self, driver_id):
        maps = request.env['route.map'].sudo().search([('driver_id.id', '=', driver_id), ('state', '!=', 'done')],
                                                        order='create_date')
        res = []
        for map_id in maps:
            lines = []
            for line in map_id.dispatch_ids:
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
            map = {
                'Id': map_id.id,
                'Name': map_id.display_name,
                'Sell': map_id.sell,
                'Lines': lines,
                'State': map_id.state
            }
            res.append(map)
            return res
        else:
            return {"message": "No tiene ninguna ruta activa"}

    @http.route('/api/add_image', type='json', auth='token', cors='*')
    def add_image(self, binary, line_id):
        line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
        request.env['ir.attachment'].sudo().create({
            'res_id': line.id
        })

    @http.route('/api/cancel', type='json', auth='token', cors='*')
    def action_cancel(self, observation, line_id):
        line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
        if line:
            line.sudo().write({
                'state': 'cancel',
                'driver_observations': observation
            })
            return {'ok': True, "message": "Pedido devuelto o cancelado"}
        else:
            return {'ok': False, "message": "Error en comunicación"}


    @http.route('/api/done', type='json', auth='token', method='GET', cors='*')
    def make_done_line(self, line_id, latitude , longitude):
        line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
        if line:
            try:
                line.sudo().write({
                    'latitude_delivery' : latitude,
                    'longitude_delivery' : longitude
                })
                line.sudo().button_done()
            except:
                return {'ok': False, "message": "Error al confirmar"}
        return {'ok': True, "message": "Pedido entregado"}
