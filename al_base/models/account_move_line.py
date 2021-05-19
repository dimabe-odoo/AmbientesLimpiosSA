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

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            if 'move_id' in values.keys():
                product_ids = self.env['account.move.line'].search([('move_id', '=', values['move_id'])]).mapped(
                    'product_id')
                if len(product_ids) > 0:
                    if 'product_id' in values.keys() and 'name' in values.keys():
                        if values['product_id'] in product_ids.ids:
                            raise models.ValidationError(
                                'No puede agregar el producto {} más de una vez'.format(values['name']))
                elif 'product_id' in values.keys() and values['product_id'] and self.product_count_to_create(values['product_id'], values_list) > 1:
                    raise models.ValidationError(
                        'No puede agregar el producto {} más de una vez'.format(values['name']))

        return super(AccountMoveLine, self).create(values_list)


    def product_count_to_create(self, product_id, values_list):
        count = 0
        for i in values_list:
            if product_id == i['product_id']:
                count += 1
        return count
