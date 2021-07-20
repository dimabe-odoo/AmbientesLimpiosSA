from odoo import models, api, fields
import json, xmltodict
from pdf417 import encode, render_image
import base64
from io import BytesIO
from py_linq import Enumerable
from ..utils.roundformat_clp import round_clp
from ..utils.get_remaining_caf import get_remaining_caf

from ..utils.generate_notification import send_notification


class AccountMove(models.Model):
    _inherit = 'account.move'

    subtotal_amount = fields.Float('Subtotal', compute="_compute_subtotal_amount")

    net_amount = fields.Float('Total Neto', compute="_compute_net_amount")

    total_exempt = fields.Float('Total Exento', compute="_compute_total_exempt")

    ted = fields.Binary('TED')

    is_jump_number = fields.Boolean('Se omitiran folios')

    document_number = fields.Char('Número de Documento')

    def _get_custom_report_name(self):
        return '%s %s' % (self.l10n_latam_document_type_id.name, self.l10n_latam_document_number)

    def action_invoice_sent(self):
        res = super(AccountMove, self).action_invoice_sent
        if not self.ted:
            self.get_ted()
        return res

    @api.model
    def _compute_subtotal_amount(self):
        for item in self:
            subtotal_amount = 0
            for line in item.invoice_line_ids:
                subtotal_amount += line.price_unit * line.quantity
            item.subtotal_amount = subtotal_amount

    @api.model
    def _compute_net_amount(self):
        for item in self:
            net_amount = 0
            for line in item.invoice_line_ids:
                net_amount += line.price_unit * line.quantity * ((100 - line.discount) / 100)
            item.net_amount = net_amount

    @api.model
    def _compute_total_exempt(self):
        for item in self:
            total_exempt = 0
            for line in item.invoice_line_ids:
                if len(line.tax_ids) == 0:
                    total_exempt += line.price_unit * line.quantity * ((100 - line.discount) / 100)
            item.total_exempt = total_exempt

    @api.depends('name')
    def _compute_l10n_latam_document_number(self):
        for item in self:
            if not item.is_jump_number:
                super(AccountMove, item)._compute_l10n_latam_document_number()
            else:
                item.l10n_latam_document_number = item.document_number
                item.name = f'{item.l10n_latam_document_type_id.doc_code_prefix} {item.document_number}'

    def get_ted(self):
        cols = 12
        while True:
            try:
                if cols == 31:
                    break
                codes = encode(self.l10n_cl_sii_barcode, cols)
                image = render_image(codes, scale=5, ratio=2)
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue())
                return img_str
            except:
                cols += 1

    @api.model
    def create(self, values):
        if 'invoice_origin' in values.keys():
            if values['invoice_origin']:
                sale_order = self.env['sale.order'].search([('name', '=', values['invoice_origin'])])
                if sale_order.l10n_latam_document_type_id:
                    values['journal_id'] = 1
                    values['l10n_latam_document_type_id'] = sale_order.l10n_latam_document_type_id.id

        return super(AccountMove, self).create(values)

    def roundclp(self, value):
        return round_clp(value)

    def custom_report_fix(self, list_report_list):
        report_linq = Enumerable(list_report_list)
        report_ids = report_linq.select(lambda x: x['id'])
        report = self.env['ir.actions.report'].search([('id', 'in', report_ids.to_list())])

        for rep in report:
            report_to_update = report_linq.first_or_default(lambda x: x['id'] == rep.id)
            if report_to_update:
                new_name = report_to_update['new_name'] if 'new_name' in report_to_update.keys() else rep.name
                new_template_name = report_to_update[
                    'template_new'] if 'template_new' in report_to_update.keys() else rep.report_name
                paperformat_id = report_to_update[
                    'paperformat_id'] if 'paperformat_id' in report_to_update.keys() else rep.paperformat_id
                print_report_name = report_to_update[
                    'print_report_name'] if 'print_report_name' in report_to_update.keys() else rep.print_report_name

                if rep.report_name != new_template_name or rep.report_file != new_template_name or rep.name != new_name or rep.paperformat_id != paperformat_id or rep.print_report_name != print_report_name:
                    rep.write({
                        'report_name': new_template_name,
                        'report_file': new_template_name,
                        'name': new_name,
                        'paperformat_id': paperformat_id,
                        'print_report_name': print_report_name
                    })
                else:
                    continue
            else:
                continue

    def action_post(self):
        res = super(AccountMove, self).action_post()
        return res

    def write(self, values):
        for item in self:
            if 'l10n_cl_dte_status' in values.keys():
                if values['l10n_cl_dte_status'] in ['accepted', 'objected']:
                    get_remaining_caf(item.l10n_latam_document_type_id.id)
            if item.l10n_cl_sii_barcode:
                values['ted'] = item.get_ted()

            if 'l10n_cl_dte_acceptation_status' in values.keys():
                message = self.get_message(values['l10n_cl_dte_acceptation_status'])
                user_group = self.env.ref('al_base.custom_noti_aceptation_dte')
                send_notification("Cambio de Estado", message, 2, user_group=user_group.user_ids, model='account.move',
                                  model_id=self.env.ref('route_map.model_account_move').id)
            res = super(AccountMove, item).write(values)

            return res

    def get_message(self, type):
        if type == 'received':
            return f"<p>Estimados.<br/><br/> Le informamos que el DTE {self.name} ha sido recibido por el cliente"
        elif type == 'ack_sent':
            return f"<p>Estimados.<br/><br/> Le informamos que el cliente acusa recibo del DTE {self.name}"
        elif type == 'claimed':
            return f"<p>Estimados.<br/><br/> Le informamos que el cliente informa reclamo del DTE {self.name}"
        elif type == 'accepted':
            return f"<p>Estimados.<br/><br/> Le informamos que el DTE {self.name} fue Aceptado por el cliente"

            return super(AccountMove, item).write(values)

    def generate_voucher(self):
        report = self.env.ref('al_base.action_custom_payment_voucher_template')
        ctx = self.env.context.copy()
        ctx['flag'] = True
        pdf = report.with_context(ctx)._render_qweb_pdf(self.id)
        file = base64.b64encode(pdf[0])
        ir_attachment_id = self.env['ir.attachment'].sudo().create({
            'name': f'Ingreso de Pago {self.name}',
            'store_fname': f'Ingreso de Pago {self.name}.pdf',
            'res_name': f'Ingreso de Pago {self.name}',
            'res_model': 'account.move',
            'res_id': self.id,
            'type': 'binary',
            'db_datas': file,
            'datas': file
        })

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):

        for move in self:

            if move.payment_state == 'invoicing_legacy':
                # invoicing_legacy state is set via SQL when setting setting field
                # invoicing_switch_threshold (defined in account_accountant).
                # The only way of going out of this state is through this setting,
                # so we don't recompute it here.
                move.payment_state = move.payment_state
                continue

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = move._get_lines_onchange_currency().currency_id

            for line in move.line_ids:
                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_to_pay += line.balance
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies or move.company_id.currency_id

            # Compute 'payment_state'.
            new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

            if move.is_invoice(include_receipts=True) and move.state == 'posted':

                if currency.is_zero(move.amount_residual):
                    reconciled_payments = move._get_reconciled_payments()
                    if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                        new_pmt_state = 'paid'
                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    new_pmt_state = 'partial'

            if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
                reverse_moves = self.env['account.move'].search(
                    [('reversed_entry_id', '=', move.id), ('state', '=', 'posted'),
                     ('move_type', '=', reverse_type)])

                # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (
                        reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                    new_pmt_state = 'reversed'

            move.payment_state = new_pmt_state

            if new_pmt_state == 'paid' and move.move_type != 'entry':
                move.generate_voucher()
