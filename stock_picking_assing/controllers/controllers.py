# -*- coding: utf-8 -*-
# from odoo import http


# class StockPickingAssing(http.Controller):
#     @http.route('/stock_picking_assing/stock_picking_assing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_picking_assing/stock_picking_assing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_picking_assing.listing', {
#             'root': '/stock_picking_assing/stock_picking_assing',
#             'objects': http.request.env['stock_picking_assing.stock_picking_assing'].search([]),
#         })

#     @http.route('/stock_picking_assing/stock_picking_assing/objects/<model("stock_picking_assing.stock_picking_assing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_picking_assing.object', {
#             'object': obj
#         })
