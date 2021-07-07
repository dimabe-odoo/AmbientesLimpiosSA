from odoo import models, fields, api
from datetime import date
from ..utils.lot_generator import generate_lot
import json, xmltodict
from pdf417 import encode, render_image
import base64
from io import BytesIO
from py_linq import Enumerable
from ..utils.roundformat_clp import round_clp
from ..utils.get_remaining_caf import get_remaining_caf


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    l10n_latam_document_type_sale_id = fields.Many2one('l10n_latam.document.type', string="Tipo de Documento")

    ted = fields.Binary('TED')

    net_amount = fields.Float('Total Neto', compute="_compute_net_amount")

    tax_amount = fields.Float('IVA', compute="_compute_tax_amount")

    amount_total = fields.Float('TOTAL', compute="_compute_amount_total")

    # invisible_btn_ted = fields.Boolean(compute="_compute_show_btn_ted", default=True)

    is_subcontract = fields.Boolean(compute='compute_is_subcontract')

    location_dest_id = fields.Many2one('stock.location', domain=[('usage', '=', 'internal'), ('active', '=', True)])

    location_id = fields.Many2one('stock.location', domain=[('usage', '=', 'internal'), ('active', '=', True)])


    def compute_is_subcontract(self):
        for item in self:
            list = Enumerable(item.move_ids_without_package)
            item.is_subcontract = list.any(lambda x: x.is_subcontract)

    def _get_custom_report_name(self):
        return '%s %s' % (
            'Guía de Despacho Electrónica',
            self.l10n_latam_document_number if self.l10n_latam_document_number else self.id)

    # @api.model
    # def _compute_show_btn_ted(self):
    #    for item in self:
    #        if item.picking_type_id.sequence_code == 'OUT':
    #            if item.ted or (item.state == 'draft' or item.state == 'cancel'):
    #                item.invisible_btn_ted = True
    #            else:
    #                item.invisible_btn_ted = False
    #        else:
    #            item.invisible_btn_ted = True

    @api.onchange('location_id')
    def onchange_location_id(self):
        for item in self:
            if item.picking_type_id.sequence_code == 'INT':
                res = {
                    'domain': {
                        'location_id': [('usage', '=', 'internal')],
                        'location_dest_id': [('usage', '=', 'internal'), ('id', '!=', self.location_id.id)]
                    }
                }
                return res

    def action_record_components(self):
        if self.partner_id.parent_subcontraction_location_id and Enumerable(self.move_ids_without_package).any(
                lambda x: x.is_subcontract):
            for move in self.move_lines:
                production = move.move_orig_ids.production_id
                production.write({
                    'location_src_id': self.partner_id.parent_subcontraction_location_id.id,
                    'location_dest_id': self.partner_id.parent_subcontraction_location_id.id,
                })
        return super(StockPicking, self).action_record_components()

    def get_ted(self, doc_id):

        if doc_id:
            doc_xml = base64.b64decode(doc_id.datas)
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

                    return img_str
                except:
                    cols += 1

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        self.show_operations = self.picking_type_id.show_operations
        self.immediate_transfer = True
        self.location_id = self.picking_type_id.warehouse_id.lot_stock_id

    @api.model
    def _compute_net_amount(self):
        for item in self:
            net_amount = 0
            for move in item.move_ids_without_package:
                for line in move.move_line_ids.sorted(key=lambda line: line.location_id.id):
                    if item.state != 'done':
                        if item.partner_id.l10n_cl_delivery_guide_price == 'product':
                            net_amount += line.product_uom_qty * line.product_id.list_price
                        elif item.partner_id.l10n_cl_delivery_guide_price == 'sale_order':
                            net_amount += line.product_uom_qty * item.sale_id.order_line.filtered(
                                lambda a: a.product_id.id == line.product_id.id).price_unit
                    if item.state == 'done':
                        if item.partner_id.l10n_cl_delivery_guide_price == 'product':
                            net_amount += line.qty_done * line.product_id.list_price
                        elif item.partner_id.l10n_cl_delivery_guide_price == 'sale_order':
                            net_amount += line.qty_done * item.sale_id.order_line.filtered(
                                lambda a: a.product_id.id == line.product_id.id).price_unit

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
                                        if item.partner_id.l10n_cl_delivery_guide_price == 'product':
                                            tax_amount += ol.product_id.list_price * ol.product_uom_qty * tax.amount / 100
                                        elif item.partner_id.l10n_cl_delivery_guide_price == 'sale_order':
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
    def create(self, values):
        self.verify_location_equal(values)
        res = super(StockPicking, self).create(values)
        sale = self.env['sale.order'].search([('name', '=', res.origin)])
        if sale:
            res.l10n_latam_document_type_sale_id = sale.l10n_latam_document_type_id
        return res

    def button_validate(self):
        if self.partner_id.parent_subcontraction_location_id:
            if self.picking_type_id.sequence_code == 'OUT':
                self.move_ids_without_package.sudo().write({
                    'location_dest_id': self.partner_id.parent_subcontraction_location_id.id
                })
                self.move_line_ids_without_package.sudo().write({
                    'location_dest_id': self.partner_id.parent_subcontraction_location_id.id
                })
        if (self.partner_id and self.partner_id.picking_warn and self.partner_id.picking_warn == 'block') or (
                self.partner_id.parent_id and self.partner_id.parent_id.picking_warn and self.partner_id.parent_id.picking_warn == 'block'):
            raise models.ValidationError(
                self.partner_id.picking_warn_msg if self.partner_id.picking_warn_msg else self.partner_id.parent_id.picking_warn_msg)
        if self.picking_type_id.sequence_code == 'IN':
            for item in self.move_line_nosuggest_ids:
                product = item.product_id
                if not item.lot_id and product.tracking == 'lot':  # todo: validar que se genere cuando sea recepcion el tipo de movimiento
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

    def roundclp(self, value):
        return round_clp(value)

    def write(self, values):
        self.verify_location_equal(values)
        if 'l10n_cl_dte_status' in values.keys():
            if values['l10n_cl_dte_status'] == 'rejected':
                get_remaining_caf(self.l10n_latam_document_type_id.id)
        if not self.ted and self.picking_type_id.sequence_code == 'OUT':
            doc_id = self.env['ir.attachment'].search(
                [('res_model', '=', 'stock.picking'), ('res_id', '=', self.id), ('name', 'like', 'SII')],
                order='create_date desc')
            if doc_id:
                values['ted'] = self.get_ted(doc_id[0])

        return super(StockPicking, self).write(values)

    def verify_location_equal(self, values):
        location_id = ''
        location_dest_id = ''
        if 'location_id' in values.keys():
            location_id = values['location_id']
        elif self.location_id:
            location_id = self.location_id.id

        if 'location_dest_id' in values.keys():
            location_dest_id = values['location_dest_id']
        elif self.location_id:
            location_dest_id = self.location_dest_id.id

        if location_dest_id != '' and location_id != '':
            if location_dest_id == location_id:
                raise models.ValidationError(
                    f'La ubicación de Origen no puede ser la misma que la ubicación de destino')

    def filter_lots(self):
        for line in self.move_line_ids_without_package:
            # quants = self.env['stock.quant'].search([('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id), ('quantity', '>', 0)])
            line.show_lot_with_stock()
            # line.lot_id.update({
            #    'domain': [('id', 'in', quants.lot_id.ids)]
            # })

            # return {'domain': {'lot_id': [('id', 'in', quants.lot_id.ids)]}}
