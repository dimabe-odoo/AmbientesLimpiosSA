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

    def get_ted(self, doc_id):

        doc_xml = base64.b64decode(doc_id.datas)
        data_dict = xmltodict.parse(doc_xml)
        if self.l10n_latam_document_type_id.code == '39':
            json_data = json.dumps(data_dict['EnvioBOLETA']['SetDTE']['DTE']['Documento']['TED'])
        else:
            json_data = json.dumps(data_dict['EnvioDTE']['SetDTE']['DTE']['Documento']['TED'])
        cols = 12
        while True:
            try:
                if cols == 31:
                    break
                codes = encode(json_data, cols)
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
                new_template_name = report_to_update['template_new'] if 'template_new' in report_to_update.keys() else rep.report_name
                paperformat_id = report_to_update['paperformat_id'] if 'paperformat_id' in report_to_update.keys() else rep.paperformat_id
                print_report_name = report_to_update['print_report_name'] if 'print_report_name' in report_to_update.keys() else rep.print_report_name

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

    def write(self, values):
        for item in self:
            if 'l10n_cl_dte_status' in values.keys():
                if values['l10n_cl_dte_status'] in ['accepted', 'objected']:
                    get_remaining_caf(item.l10n_latam_document_type_id.id)
            if not item.ted:
                doc_id = self.env['ir.attachment'].search(
                    [('res_model', '=', 'account.move'), ('res_id', '=', item.id), ('name', 'like', 'SII')],
                    order='create_date desc')
                if doc_id and len(doc_id) > 0:
                    values['ted'] = item.get_ted(doc_id[0])
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
        #payment_id = self.env['account.payment'].search([('ref','=', self.payment_reference)])
        if self.payment_state == 'paid':
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
        for item in self:
            res = super(AccountMove, item)._compute_amount()

            if item.payment_state == 'paid':
                item.generate_voucher()

            return res


