from odoo import fields, models, api
from datetime import datetime


class CustomPersonalMovements(models.Model):
    _name = 'custom.personal.movements'

    personal_movements = fields.Selection([('0', 'Sin Movimiento en el Mes'),
                                           ('1', 'Contratación a plazo indefinido'),
                                           ('2', 'Retiro'),
                                           ('3', 'Subsidios (L Médicas)'),
                                           ('4', 'Permiso Sin Goce de Sueldos'),
                                           ('5', 'Incorporación en el Lugar de Trabajo'),
                                           ('6', 'Accidentes del Trabajo'),
                                           ('7', 'Contratación a plazo fijo'),
                                           ('8', 'Cambio Contrato plazo fijo a plazo indefinido'),
                                           ('11', 'Otros Movimientos (Ausentismos)'),
                                           ('12', 'Reliquidación, Premio, Bono')
                                           ], 'Movimientos Personal', default="0")

    date_start = fields.Date('Fecha Inicio')

    date_end = fields.Date('Fecha Final')

    payslip_id = fields.Many2one('hr.payslip', auto_join=True)

    def create(self, values):
        for value in values:
            date_start = fields.Date.from_string(value['date_start'])
            date_end = fields.Date.from_string(value['date_end'])
            if date_start > date_end:
                raise models.UserError('La fecha inicio no puede ser mayor a la fecha final')
            movement = self.env['custom.personal.movements'].search(
                [('personal_movements', '=', value['personal_movements']), ('payslip_id', '=', value['payslip_id'])])
            if movement:
                if date_start <= movement.date_end <= date_end or date_start >= movement.date_start >= date_end:
                    raise models.UserError('Ya existe un movimiento personal vigente en el rango de fecha ingresado')
        res = super(CustomPersonalMovements, self).create(values)
        return res
