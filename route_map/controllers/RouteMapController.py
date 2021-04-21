from odoo import http
from odoo.http import request


class RouteMapController(http.Controller):

    @http.route('/api/route_map', type='json', method='GET', cors='*')
    def get_route_map(self, driver_id):
        map_id = request.env['route.map'].sudo().search([('driver_id.id', '=', driver_id), ('state', '!=', 'done')])
        if map_id:
            lines = []
            for line in map_id.dispatch_ids:
                lines.append({
                    'Id': line.id,
                    'Destiny': line.partner_id.name,
                    'Address': line.address_to_delivery,
                    'LatitudeDestiny': line.partner_id.partner_latitude,
                    'LongitudeDestiny': line.partner_id.partner_longitude
                })
            res = {
                'Id': map_id.id,
                'Sell': map_id.sell,
                'Lines': lines
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
    def setobservation(self, observation, line_id):
        for item in self:
            line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
            line.sudo().write({
                'driver_observations':observation
            })

    @http.route('/api/done', type='json', method='GET', cors='*')
    def make_done_line(self, line_id):
        line = request.env['route.map.line'].sudo().search([('id', '=', line_id)])
        if line:
            line.button_done()
        return {"message": "Pedido entregado"}
