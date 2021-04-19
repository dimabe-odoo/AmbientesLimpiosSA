# -*- coding: utf-8 -*-
{
    'name': "Módulo base para implementación en ambientes limpios",

    'summary': """
        Módulo adaptado a las necesidades de Ambientes Limpios """,

    'description': """
        Modificaciones necesarias para cumplir con los requerimientos de la empresa ambientes limpios.
    """,

    'author': "Dimabe Ltda",
    'website': "https://www.dimabe.cl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'stock', 'sale','account','mrp','mrp_workorder'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_product.xml',
        'views/product_template.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'reports/product_label_barcode.xml',
        'reports/purchase_order.xml',
        'views/res_company.xml',
        'views/stock_picking.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}