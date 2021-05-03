from odoo import fields, models, api


class StockPickings(models.Model):
    _rec_name = 'display_name'
    _inherit = 'stock.picking'

    is_delivered = fields.Boolean()

    map_id = fields.Many2one('route.map', string='Hoja de Ruta')

    display_name = fields.Char('Nombre a mostrar', compute='compute_display_name')

    def compute_display_name(self):
        for item in self:
            if 'active_model' in self.env.context.keys():
                model = self.env.context['active_model']
                if model != 'route.map.line':
                    item.display_name = item.name
            else:
                item.display_name = f'Cliente :  {item.sale_id.partner_id.display_name} Factura : {",".join(item.sale_id.invoice_ids.mapped("name"))} Pedido {item.sale_id.name}'
