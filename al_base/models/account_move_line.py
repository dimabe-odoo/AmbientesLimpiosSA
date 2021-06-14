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
            item.subtotal_with_taxes = item.price_subtotal + (item.taxes_amount * item.quantity)


