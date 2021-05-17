from odoo import models, api, fields

class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    taxes_amount = fields.Float('Monto Impuesto', compute="_compute_taxes_amount")

    price_unit_with_discount = fields.Float('Precio Unit. con Descuento', compute="_compute_price_unit_with_discount")

    subtotal_with_taxes = fields.Float('Subtotal con Impuesto', compute="_compute_subtotal_with_taxes")

    @api.model
    def _compute_price_unit_with_discount(self):
        for item in self:
            item.price_unit_with_discount = item.price_unit - (item.price_unit * item.discount / 100)

    @api.model
    def _compute_taxes_amount(self):
        for item in self:
            taxes_amount = 0
            for tax in item.tax_ids:
                taxes_amount += item.price_unit_with_discount * tax.amount / 100

            item.taxes_amount = taxes_amount

    @api.model
    def _compute_subtotal_with_taxes(self):
        for item in self:
            item.subtotal_with_taxes = item.price_subtotal + item.taxes_amount

<<<<<<< HEAD

=======
    # @api.model
    # def create(self, values):
    #     if 'move_id' in values.keys():
    #         product_ids = self.env['account.move.line'].search([('move_id','=',values['move_id'])]).mapped('product_id')
    #         if len(product_ids) > 0:
    #             if 'product_id' in values.keys() and 'name' in values.keys():
    #                 if values['product_id'] in product_ids.ids:
    #                     raise models.ValidationError('No puede agregar el producto {} más de una vez'.format(values['name']))
    #
    #     return super(AccountMoveLine, self).create(values)
>>>>>>> 887dc2b31eb267b45b49c59218a9a32f77a7e702
