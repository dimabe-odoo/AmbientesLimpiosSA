from odoo import fields, models, api
from ..utils.valid_range_approve import valid_range


class CustomRangeApproveSale(models.Model):
    _name = 'custom.range.approve.sale'

    name = fields.Char('Nombre')

    user_ids = fields.Many2many(comodel_name="res.users", relation="custom_user_rel", string='Usuarios')

    user_configuration = fields.Selection([('leader', 'Por Lider de Equipo Venta'), ('user', 'Por Usuario')],
                                          string="Configuración de Usuario", default="leader",
                                          help="Por Lider de Equipo Venta: Solo pueden aprobar por descuento, los usuarios en la lista que sean lideres de algún equipo de Venta, la cual solo podrán realizar el flujo de venta (Presupuesto -> Aprobación por Descuento) los miembros de de los equipos de venta asociaso a los líderes \nPor Usuario: Todos los usuarios pertenecientes al grupo Vendedor puede realizar el flujo de venta (Presupuesto -> Aprobación por Descuento). Todos los usuarios agregados en la lista pueden aprobar por descuento")

    min_amount = fields.Integer('Monto Minimo')

    max_amount = fields.Integer('Monto Máximo', help='Si no tiene monto máximo, dejar en 0')

    external_user_ids = fields.Many2many(comodel_name="res.users", relation="custom_external_user_rel",
                                         string='Usuarios (Apoyo Vendedor)',
                                         help="Usuarios que pueden generar un pedido de Venta (cambio de estado Presupuesto -> Aprobación por Descuento) que no se encuentran en algún equipo de Venta")

    @api.model
    def create(self, values):
        res = super(CustomRangeApproveSale, self).create(values)
        if values['max_amount'] > values['min_amount'] or values['max_amount'] == 0:
            if self.valid_range_create(values, res.id):
                return res
        else:
            raise models.ValidationError(
                'Monto máximo debe ser mayor que el monto mínimo, excepto si el monto máximo no tiene límite, éste debe ser 0')

    def write(self, values):
        res = super(CustomRangeApproveSale, self).write(values)
        if 'min_amount' not in values.keys():
            values['min_amount'] = self.min_amount
        if 'max_amount' not in values.keys():
            values['max_amount'] = self.max_amount
        if 'max_amount' in values.keys() and 'min_amount' in values.keys():
            if values['max_amount'] > values['min_amount'] or values['max_amount'] == 0:
                if self.valid_range_write(values):
                    return res
            else:
                raise models.ValidationError(
                    'Monto máximo debe ser mayor que el monto mínimo, excepto si el monto máximo no tiene límite, éste debe ser 0')

    def valid_range_create(self, values, id):
        range_ids = self.env['custom.range.approve.sale'].search([('id', '!=', id)])
        return valid_range(values, range_ids)

    def valid_range_write(self, values):
        range_ids = self.env['custom.range.approve.sale'].search([('id', '!=', self.id)])
        return valid_range(values, range_ids)
