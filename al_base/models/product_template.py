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
                if 'al_dun' in value.keys():
                    if value['al_dun']:
                        data = check_duplicate_record.check_duplicate(value['al_dun'], 'al_dun', 'DUN', self._inherit,
                                                                      'create')
                        if data['have_record']:
                            raise models.ValidationError(data['message'])
                if 'default_code' in value.keys():
                    if value['default_code']:
                        data = check_duplicate_record.check_duplicate(value['default_code'], 'default_code', 'SKU',
                                                                      self._inherit,
                                                                      'create')
                        if data['have_record']:
                            raise models.ValidationError(data['message'])
                if 'barcode' in value.keys():
                    if value['barcode']:
                        data = check_duplicate_record.check_duplicate(value['barcode'], 'barcode', 'Codigo de Barras',
                                                                      self._inherit,
                                                                      'create')
                        if data['have_record']:
                            raise models.ValidationError(data['message'])
        else:
            if 'al_dun' in values.keys():
                if values['al_dun']:
                    data = check_duplicate_record.check_duplicate(values['al_dun'], 'al_dun', 'DUN', self._inherit,
                                                                  'create')
                    if data['have_record']:
                        raise models.ValidationError(data['message'])
            if 'default_code' in values.keys():
                if values['default_code']:
                    data = check_duplicate_record.check_duplicate(values['default_code'], 'default_code', 'SKU',
                                                                  self._inherit,
                                                                  'create')
                    if data['have_record']:
                        raise models.ValidationError(data['message'])
            if 'barcode' in values.keys():
                if values['barcode']:
                    data = check_duplicate_record.check_duplicate(values['barcode'], 'barcode', 'Codigo de Barras',
                                                                  self._inherit,
                                                                  'create')
                    if data['have_record']:
                        raise models.ValidationError(data['message'])
        return super(ProductTemplate, self).create(values)

    def write(self,values):
        if isinstance(values, list):
            for value in values:
                if 'al_dun' in value.keys():
                    if value['al_dun']:
                        data = check_duplicate_record.check_duplicate(value['al_dun'], 'al_dun', 'DUN', self._inherit,
                                                                      'write',id_record=self.id)
                        if data['have_record']:
                            raise models.ValidationError(data['message'])
                if 'default_code' in value.keys():
                    if value['default_code']:
                        data = check_duplicate_record.check_duplicate(value['default_code'], 'default_code', 'SKU',
                                                                      self._inherit,
                                                                      'write',id_record=self.id)
                        if data['have_record']:
                            raise models.ValidationError(data['message'])
                if 'barcode' in value.keys():
                    if value['barcode']:
                        data = check_duplicate_record.check_duplicate(value['barcode'], 'barcode', 'Codigo de Barras',
                                                                      self._inherit,
                                                                      'write',id_record=self.id)
                        if data['have_record']:
                            raise models.ValidationError(data['message'])
        else:
            if 'al_dun' in values.keys():
                if values['al_dun']:
                    data = check_duplicate_record.check_duplicate(values['al_dun'], 'al_dun', 'DUN', self._inherit,
                                                                  'write',id_record=self.id)
                    if data['have_record']:
                        raise models.ValidationError(data['message'])
            if 'default_code' in values.keys():
                if values['default_code']:
                    data = check_duplicate_record.check_duplicate(values['default_code'], 'default_code', 'SKU',
                                                                  self._inherit,
                                                                  'write',id_record=self.id)
                    if data['have_record']:
                        raise models.ValidationError(data['message'])
            if 'barcode' in values.keys():
                if values['barcode']:
                    data = check_duplicate_record.check_duplicate(values['barcode'], 'barcode', 'Codigo de Barras',
                                                                  self._inherit,
                                                                  'write',id_record=self.id)
                    if data['have_record']:
                        raise models.ValidationError(data['message'])
        return super(ProductTemplate, self).write(values)