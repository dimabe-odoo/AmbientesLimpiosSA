# -*- coding: utf-8 -*-
{
    "name": """Chile - Electronic Receipt""",
    'version': '1.0',
    'category': 'Localization/Chile',
    'sequence': 12,
    'author':  'Blanco Martín & Asociados',
    'website': 'http://blancomartin.cl',
    'depends': ['l10n_cl_edi'],
    'data': [
        'data/cron.xml',
        'template/daily_sales_book_template.xml',
        'template/dte_template.xml',
        'security/ir.model.access.csv',
        'security/l10n_cl_edi_boletas_security.xml',
        'views/l10n_cl_daily_sales_book_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
