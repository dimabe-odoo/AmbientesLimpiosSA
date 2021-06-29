from odoo import models, fields, api
from ..utils import check_duplicate_record


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    al_sku = fields.Char(string='Código Sysgestion')
    al_dun = fields.Char(string='DUN')

    @api.model
    def create(self, values):
        if isinstance(values, list):
            for value in values:
                if 'default_code' in value.keys():
                    if value['default_code']:
                        data = check_duplicate_record.check_duplicate(value['default_code'], 'default_code', 'SKU',
                                                                      self._inherit,
                                                                      'create')
                        if data['have_record']:
                            raise models.ValidationError(data['message'])
        else:
            if 'default_code' in values.keys():
                if values['default_code']:
                    data = check_duplicate_record.check_duplicate(values['default_code'], 'default_code', 'SKU',
                                                                  self._inherit,
                                                                  'create')
                    if data['have_record']:
                        raise models.ValidationError(data['message'])
        return super(ProductTemplate, self).create(values)

    def write(self,values):
        if isinstance(values, list):
            for value in values:
                if 'default_code' in value.keys():
                    if value['default_code']:
                        data = check_duplicate_record.check_duplicate(value['default_code'], 'default_code', 'SKU',
                                                                      self._inherit,
                                                                      'write',id_record=self.id)
                        if data['have_record']:
                            raise models.ValidationError(data['message'])
        else:
            if 'default_code' in values.keys():
                if values['default_code']:
                    data = check_duplicate_record.check_duplicate(values['default_code'], 'default_code', 'SKU',
                                                                  self._inherit,
                                                                  'write',id_record=self.id)
                    if data['have_record']:
                        raise models.ValidationError(data['message'])
        return super(ProductTemplate, self).write(values)