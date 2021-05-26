# -*- coding: utf-8 -*-
# from odoo import http


# class RouteMap(http.Controller):
#     @http.route('/route_map/route_map/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/route_map/route_map/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('route_map.listing', {
#             'root': '/route_map/route_map',
#             'objects': http.request.env['route_map.route_map'].search([]),
#         })

#     @http.route('/route_map/route_map/objects/<model("route_map.route_map"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('route_map.object', {
#             'object': obj
#         })
