from odoo import models, api, fields
import json, xmltodict
from pdf417 import encode, render_image
import base64
from io import BytesIO

class AccountMove(models.Model):
    _inherit = 'account.move'

    subtotal_amount = fields.Float('Subtotal', compute="_compute_subtotal_amount")

    net_amount = fields.Float('Total Neto', compute="_compute_net_amount")

    total_exempt = fields.Float('Total Exento', compute="_compute_total_exempt")

    ted = fields.Binary('TED')

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

    #@api.model
    #def action_post(self):
    #    res = super(AccountMove, self).action_post
    #    doc_xml = self.env['ir.attachment'].search([('res_model','=','account.move'),('res_id','=',self.id),('SII','in','name')])
    #    return res

    def get_ted(self):
        doc_id = self.env['ir.attachment'].search([('res_model', '=', 'account.move'), ('res_id', '=', self.id), ('SII','in','name')]).db_datas
        doc_xml = base64.standard_b64decode(doc_id)
        base64.b64
        with open(doc_xml) as xml_file:
            data_dict = xmltodict.parse(xml_file.read())
            json_data = json.dumps(data_dict['EnvioDTE']['SetDTE']['DTE']['Documento']['TED'])
            # print(data_dict['EnvioDTE']['SetDTE']['DTE']['Documento']['TED'])
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
                    self.write({'ted': img_str})
                    break
                except:
                    cols += 1

    @api.model
    def create(self, values):
        if 'invoice_origin' in values.keys():
            if values['invoice_origin']:
                sale_order = self.env['sale.order'].search([('name','=',values['invoice_origin'])])
                if sale_order.l10n_latam_document_type_id:
                    values['journal_id'] = 1
                    values['l10n_latam_document_type_id'] = sale_order.l10n_latam_document_type_id.id

        return super(AccountMove, self).create(values)
