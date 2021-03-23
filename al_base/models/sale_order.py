from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type')
<<<<<<< HEAD

=======
    
>>>>>>> 624b6c5d0f0f43b245365de2cabdbd757ab505c4
