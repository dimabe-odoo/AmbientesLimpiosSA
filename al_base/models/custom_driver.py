from odoo import fields, models

class CustomDriver(models.Model):
    _name = 'custom.driver'

    name = fields.Char('Nombre')

    rut = fields.Char('RUT')

    phone = fields.Char('Numero')

