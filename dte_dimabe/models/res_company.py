from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    economic_activities = fields.Many2many('custom.economic.activity', string='Actividades de la empresa')
    
    dte_url = fields.Char(string='URL portal de Facturacion',
                          help='',
                          required=True,
                          default='https://services.dimabe.cl/api/dte/emite')

    resolution_date = fields.Date(string='Fecha Resolución',
                         help='Fecha de Resolución entregada por el SII',
                         required=True,
                         default='2014-08-22')
    resolution_number = fields.Integer(string='Numero Resolución',
                                   help='Número de Resolución entregada por el SII',
                                   required=True,
                                   default='80')
                                   
    dte_hash = fields.Char(string='ApiKey Cliente',
                                    help='ApiKey Cliente Facturador Electrónico',
                                    required=True,
                                    default='')
    dte_customer_code = fields.Char(string='Código Cliente',
                                    help='Código Cliente Facturador Electrónico',
                                    required=True,
                                    default='')