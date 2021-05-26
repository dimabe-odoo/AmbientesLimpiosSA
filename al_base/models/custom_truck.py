from odoo import fields,models
from odoo.models import Model
from odoo.fields import Char , Boolean

class CustomTruck(Model):
    _name = 'custom.truck'

    name = Char('Patente')

    is_truck = Boolean('Es Camion')

