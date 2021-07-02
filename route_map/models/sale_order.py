from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_publish_ids  =fields.Many2many('account.move')

    def add_posted_invoices(self):
        self.write({
            'invoice_publish_ids': [(4,i.id) for i in self.invoice_ids.filtered(lambda x: x.state == 'posted')]
        })
