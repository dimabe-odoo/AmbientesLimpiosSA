from odoo import models, api, fields
from ..utils.rut_helper import RutHelper


class ResPartner(models.Model):
    _inherit = 'res.partner'


