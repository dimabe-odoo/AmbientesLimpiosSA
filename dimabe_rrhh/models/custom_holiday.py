from odoo import models,fields
from datetime import datetime
import requests

class CustomHolidays(models.Model):
    _name = 'custom.holidays'

    name = fields.Char('Nombre')

    date = fields.Date('Fecha')

    type = fields.Selection([('Civil', 'Civil'),('Religioso','Religioso')])

    inalienable = fields.Boolean('Irrenunciable')


    def get_holidays_by_year(self):
        res = requests.request(
            'GET',
            'https://apis.digital.gob.cl/fl/feriados/{}'.format(datetime.now().strftime('%Y'))
        )

        if 'error' in res.keys():
            if res['error'] = 'true':
                raise models.ValidationError('Error: {}'.format(res.message))
        else:
            if len(res) > 0:
                for item in res:
                    if 'fecha' in item.keys():
                        holiday_id = self.env['custom.holidays'].search([('date','=', item['nombre'])])
                        if len(holiday_id) == 0:
                            self.env['custom.holidays'].create({
                                'name' : item['nombre'],
                                'date' : item['fecha'],
                                'type' : item['tipo'],
                                'inalienable' : False if item['irrenunciable'] == '0' else True
                            })
