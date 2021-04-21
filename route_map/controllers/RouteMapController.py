from odoo import http
from odoo.http import request


class RouteMapController(http.Controller):

    @http.route('/api/route_map', type='json', auth='token', method='GET', cors='*')
    def get_route_map(self, driver_id):
        map_id = request.env['route.map'].sudo().search([('driver_id.id', '=', driver_id), ('state', '!=', 'done')],
                                                        order='create_date', limit=1)
        if map_id:
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
            res = {
                'Id': map_id.id,
                'Sell': map_id.sell,
                'Lines': lines,
                'State': map_id.state
            }
            return res
        else:
            return {"message": "No tiene ninguna ruta activa"}

    @http.route('/api/add_image', type='json', auth='token', cors='*')
    def add_image(self, binary, line_id):
        line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
        request.env['ir.attachment'].sudo().create({
            'res_id': line.id
        })

    @http.route('/api/setobservation', type='json', auth='token', cors='*')
    def set_observation(self, observation, line_id):
        for item in self:
            line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
            line.sudo().write({
                'driver_observations': observation
            })

    @http.route('/api/done', type='json', auth='token', method='GET', cors='*')
    def make_done_line(self, line_id):
        line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
        if line:
            try:
                line.button_done()
            except:
                return {'ok': False, "message": "Error al confirmar"}
        return {'ok': True, "message": "Pedido entregado"}
