# -*- coding: utf-8 -*-
{
    'name': "Dimabe Dte",

    'summary': """
        Módulo desarrollado para emitir facturas desde Odoo a servicios http de Dimabe
        """,

    'description': """
        
    """,

    'author': "Dimabe Ltda",
    'website': "https://www.dimabe.cl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/custom_economic_activity.xml',
        'views/res_company.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}