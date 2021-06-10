from odoo import models, api, fields
import json, xmltodict
from pdf417 import encode, render_image
import base64
from io import BytesIO
from ..utils.roundformat_clp import round_clp
from ..utils.get_remaining_caf import get_remaining_caf


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

    def write(self, values):
        if 'l10n_cl_dte_status' in values.keys():
            if values['l10n_cl_dte_status'] in ['accepted', 'objected']:
                get_remaining_caf(self.l10n_latam_document_type_id.id)
        if not self.ted:
            doc_id = self.env['ir.attachment'].search(
                [('res_model', '=', 'account.move'), ('res_id', '=', self.id), ('name', 'like', 'SII')],
                order='create_date desc')
            if doc_id:
                values['ted'] = self.get_ted(doc_id[0])

        return super(AccountMove, self).write(values)
