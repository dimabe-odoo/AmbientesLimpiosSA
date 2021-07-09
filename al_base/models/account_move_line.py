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


    def _l10n_cl_get_line_amounts(self):

        res = super(AccountMoveLine, self)._l10n_cl_get_line_amounts()

        if self.discount > 0 and self.move_id.l10n_latam_document_type_id.code == '39':
            res['price_item'] = res['price_item'] + (float(res['total_discount']) / self.quantity)

        return res
'''

    def create(self, values_list):
        res = super(AccountMoveLine, self).create(values_list)
        move_id = 0
        for values in values_list:
            if 'move_id'in values.keys() and values['move_id']:
                move_id = values['move_id']
                break

        count_line = self.env['account.move.line'].search([('move_id', '=', move_id), ('exclude_from_invoice_tab', '=', False)])

        if len(count_line) > 20:
            raise models.ValidationError('No puede ingresar más de 20 lineas de productos')

        return res
'''

