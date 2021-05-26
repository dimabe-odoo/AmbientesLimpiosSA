from odoo import models, fields, http
from datetime import datetime
import urllib3
import json


class CustomHolidays(models.Model):
    _name = 'custom.holidays'

    name = fields.Char('Nombre')

    date = fields.Date('Fecha')

    type = fields.Selection([('Civil', 'Civil'), ('Religioso', 'Religioso')])

    inalienable = fields.Boolean('Irrenunciable')

    def get_holidays_by_year(self):
        url = 'https://apis.digital.gob.cl/fl/feriados/{}'.format(str(datetime.now().year))
        http = urllib3.PoolManager()
        res = http.request('GET', url)

        try:
            res = json.loads(res.data.decode('utf-8'))

            if len(res) > 0:
                if len(res) == 2:
                    if 'error' in res.keys() and 'message' in res.keys():
                        if res['error'] == True:
                            raise models.ValidationError('Error: {}'.format(res['message']))
                else:
                    for item in res:
                        if 'nombre' in item and item['nombre'] == 'Todos los Días Domingos':
                            continue
                        if 'fecha' in item:
                            holiday_id = self.env['custom.holidays'].search([('date', '=', item['fecha'])])
                            if len(holiday_id) == 0:
                                self.env['custom.holidays'].create({
                                    'name': item['nombre'],
                                    'date': item['fecha'],
                                    'type': item['tipo'],
                                    'inalienable': False if item['irrenunciable'] == '0' else True
                                })
        except Exception as e:
            raise models.ValidationError(f'{e} Favor contactar con el administrador de Sistema')
