from odoo import models, fields, api
from datetime import date
from ..utils.lot_generator import generate_lot
import json, xmltodict
from pdf417 import encode, render_image
import base64
from io import BytesIO


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    l10n_latam_document_type_sale_id = fields.Many2one('l10n_latam.document.type', string="Tipo de Documento")

    ted = fields.Binary('TED')

    net_amount = fields.Float('Total Neto', compute="_compute_net_amount")

    tax_amount = fields.Float('IVA', compute="_compute_tax_amount")

    amount_total = fields.Float('TOTAL', compute="_compute_amount_total")

    invisible_btn_ted = fields.Boolean(compute="_compute_show_btn_ted", default=True)

    def _get_custom_report_name(self):
        return '%s %s' % ('Guía de Despacho Electrónica', self.l10n_latam_document_number if self.l10n_latam_document_number else self.id)

    @api.model
    def _compute_show_btn_ted(self):
        for item in self:
            if item.ted != False or (item.state == 'draft' or item.state == 'cancel'):
                item.invisible_btn_ted = True
            else:
                item.invisible_btn_ted = False

    def get_ted(self):
        doc_id = self.env['ir.attachment'].search(
            [('res_model', '=', 'stock.picking'), ('res_id', '=', self.id), ('name', 'like', 'SII')]).datas
        if doc_id:
            doc_xml = base64.b64decode(doc_id).decode('utf-8')
            data_dict = xmltodict.parse(doc_xml)
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
                    self.write({'ted': img_str})
                    break
                except:
                    cols += 1
        else:
            raise models.ValidationError(
                'No se puede generar código de barra 2D ya que aun no se ha generado la Guía de Despacho')

    @api.model
    def _compute_net_amount(self):
        for item in self:
            net_amount = 0
            for move in item.move_ids_without_package:
                for line in move.move_line_ids.sorted(key=lambda line: line.location_id.id):
                    if item.state != 'done':
                        net_amount += line.product_uom_qty * line.product_id.list_price
                    if item.state == 'done':
                        net_amount += line.qty_done * line.product_id.list_price

            item.net_amount = int(net_amount)

    @api.model
    def _compute_tax_amount(self):
        for item in self:
            tax_amount = 0
            for move in item.move_ids_without_package:
                for line in move.move_line_ids.sorted(key=lambda line: line.location_id.id):
                    for ol in item.sale_id.order_line:
                        if ol.product_id.id == line.product_id.id:
                            if len(ol.tax_id) > 0:
                                for tax in ol.tax_id:
                                    if tax.l10n_cl_sii_code == 14:
                                        tax_amount += ol.price_unit * ol.product_uom_qty * tax.amount / 100
            item.tax_amount = int(tax_amount)

    @api.model
    def _compute_amount_total(self):
        for item in self:
            item.amount_total = int(item.net_amount + item.tax_amount)

    def get_last_lot(self):
        now = date.today()
        last_lot = self.env['stock.production.lot'].sudo().search([('name', 'like', '-')], order='id desc', limit=1)
        if last_lot:
            lot = last_lot.name
            if len(lot.split('-')) == 2:
                return generate_lot(lot)
        return generate_lot()

    @api.model
    def create(self,values):
        res = super(StockPicking, self).create(values)
        sale = self.env['sale.order'].search([('name','=',res.origin)])
        if sale:
            res.l10n_latam_document_type_sale_id = sale.l10n_latam_document_type_id
        return res

    def button_validate(self):
        if (self.partner_id and self.partner_id.picking_warn and self.partner_id.picking_warn == 'block') or (self.partner_id.parent_id and self.partner_id.parent_id.picking_warn and self.partner_id.parent_id.picking_warn == 'block'):
            raise models.ValidationError(self.partner_id.picking_warn_msg if self.partner_id.picking_warn_msg else self.partner_id.parent_id.picking_warn_msg)
        if self.picking_type_id.sequence_code == 'IN':
            for item in self.move_line_nosuggest_ids:
                    product = item.product_id
                    if not item.lot_id and product.tracking == 'lot': # todo: validar que se genere cuando sea recepcion el tipo de movimiento
                        lot = self.get_last_lot()
                        if lot:
                            created_lot = self.env['stock.production.lot'].sudo().create({
                                'name': lot,
                                'product_id': item.product_id.id,
                                'product_qty': item.qty_done,
                                'company_id': self.env.user.company_id.id,
                                'supplier_lot': item.supplier_lot if item.supplier_lot else ''
                            })
                            item.write({
                                'lot_id': created_lot.id
                            })

        return super(StockPicking, self).button_validate()  
