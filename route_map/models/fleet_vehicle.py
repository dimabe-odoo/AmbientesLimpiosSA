from odoo import fields, models, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    transport_value = fields.Float('Valor de Transporte')
