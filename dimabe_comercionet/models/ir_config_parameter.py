from odoo import fields, models, api


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    is_password = fields.Boolean('Esta almacenado una contraseña')

    password = fields.Char('Contraseña')

    @api.depends('password')
    def add_value_from_password(self):
        self.value = "Esta almacenando una contraseña"