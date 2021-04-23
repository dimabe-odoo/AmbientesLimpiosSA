from odoo import models, fields

class SaleOrderComercionet(models.Model):
    _name = 'sale.order.comercionet'
    _rec_name = 'purchase_order'
    purchase_order = fields.Char('Orden de compra')
    client_code_comercionet = fields.Char('Casilla Comercionet')
    sale_order_id = fields.Many2one('sale.order', string='Nota de Venta')
    comercionet_line_id = fields.One2many('sale.order.comercionet.line', 'comercionet_id')

    

class SaleOrderComercionetLine(models.Model):
    _name = 'sale.order.comercionet.line'
    number = fields.Integer('Linea de Pedido')
    product_code = fields.Char('Código Producto (DUN)')
    final_price = fields.Integer('Precio Final')
    price = fields.Integer('Precio Unitario')
    quantity = fields.Integer('Cantidad')
    discount_percent = fields.Float('Descuento')
    comercionet_id = fields.Many2one('sale.order.comercionet')




    
