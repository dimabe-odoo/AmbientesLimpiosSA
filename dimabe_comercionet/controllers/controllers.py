# -*- coding: utf-8 -*-
# from odoo import http


# class DimabeComercionet(http.Controller):
#     @http.route('/dimabe_comercionet/dimabe_comercionet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dimabe_comercionet/dimabe_comercionet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dimabe_comercionet.listing', {
#             'root': '/dimabe_comercionet/dimabe_comercionet',
#             'objects': http.request.env['dimabe_comercionet.dimabe_comercionet'].search([]),
#         })

#     @http.route('/dimabe_comercionet/dimabe_comercionet/objects/<model("dimabe_comercionet.dimabe_comercionet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dimabe_comercionet.object', {
#             'object': obj
#         })
