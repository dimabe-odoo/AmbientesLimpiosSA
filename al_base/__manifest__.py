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
    'depends': ['base', 'product', 'stock', 'sale','account','mrp','mrp_workorder','l10n_cl_edi','quality'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/product_product.xml',
        'views/product_template.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'reports/purchase_order.xml',
        'views/res_company.xml',
        'views/stock_picking.xml',
        'views/account_move.xml',
        'views/purchase_order.xml',
        'views/account_move_reversal.xml',
        'reports/invoice.xml',
        'views/custom_range_approve_sale.xml',
        'views/custom_range_approve_purchase.xml',
        'data/custom_collection_group_data.xml',
        'views/custom_collection_group.xml',
        'views/mrp_production.xml',
        #'data/action_server.xml',
        'reports/product_lot_barcode.xml',
        'reports/sale_order_report.xml',
        'views/l10n_latam_document_type_view.xml',
        'views/custom_remaining_caf_group.xml',
        'views/main_data_change_report.xml',
        'reports/payment_voucher.xml',
        'views/account_payment_register_view.xml',
        'views/account_payment.xml',
        'data/account_check_inbound.xml',
        'views/custom_change_status_dte.xml',
        'reports/report_picking_odoo.xml',
        'data/ir_cron_sale_order.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}