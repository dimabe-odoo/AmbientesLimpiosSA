from odoo import fields, models, api
import xlsxwriter
import base64


class WizardExcelReport(models.Model):
    _name = 'wizard.excel.report'

    def create_total_order(self):
        file = 'total_order.xlsx'
        workbook = xlsxwriter.Workbook(file)
        formats = self.get_formats(workbook)
        sheet = workbook.add_worksheet('Total Pedido')
        sheet = self.set_title(['N°.Pedido', 'Fecha NV', 'N° OC', 'N° Factura', 'RUT', 'Cliente', 'Vendedor', 'Codigo',
                                'Descripcion', 'Precio Unitario', 'Solicitado', 'Despachado', 'Pendiente',
                                'Monto Pendiente'], sheet)
        sale_order_line = self.env['sale.order.line'].sudo().search(
            [('order_id.state', '!=', 'cancel'), ('order_id.invoice_publish_ids', '!=', False)], order='order_id')
        row = 1
        col = 0
        for line in sale_order_line:
            qty_remaing = line.product_uom_qty - line.qty_delivered
            remaing_value = line.price_unit * qty_remaing
            sheet.write(row, col, line.order_id.name)
            col += 1
            sheet.write(row, col, line.order_id.date_order, formats['date_format'])
            col += 1
            sheet.write(row, col, line.order_id.client_order_ref if line.order_id.client_order_ref else '')
            col += 1
            sheet.write(row, col, ' '.join(
                line.order_id.invoice_publish_ids.filtered(lambda x: 'refund' not in x.move_type).mapped('name')))
            col += 1
            sheet.write(row, col,
                        line.order_id.partner_shipping_id.vat if line.order_id.partner_shipping_id.vat else '')
            col += 1
            sheet.write(row, col, line.order_id.partner_shipping_id.display_name)
            col += 1
            sheet.write(row, col, line.order_id.user_id.display_name)
            col += 1
            sheet.write(row, col, line.product_id.default_code)
            col += 1
            sheet.write(row, col, line.product_id.name)
            col += 1
            sheet.write(row, col, line.price_unit)
            col += 1
            sheet.write(row, col, line.product_uom_qty)
            col += 1
            sheet.write(row, col, line.qty_delivered)
            col += 1
            sheet.write(row, col, qty_remaing if qty_remaing > 0 else '-')
            col += 1
            sheet.write(row, col, remaing_value if qty_remaing > 0 else '-')
            col = 0
            row += 1
        workbook.close()
        with open(file, "rb") as file:
            file_base64 = base64.b64encode(file.read())
        report_name = f'Report de Total Pedido.xlsx'
        attachment = self.env['ir.attachment'].sudo().create({
            'name': report_name,
            'store_fname': report_name,
            'datas': file_base64
        })
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment.id),
            'target': 'new'
        }
        return action

    def get_formats(self, workbook):
        date = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        return {'date_format': date}

    def set_title(self, titles, sheet):
        row = 0
        col = 0
        for title in titles:
            sheet.write(row, col, title)
            col += 1
        return sheet
