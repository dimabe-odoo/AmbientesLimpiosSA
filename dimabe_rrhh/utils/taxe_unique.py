from bs4 import BeautifulSoup
from datetime import date
import requests
from odoo import models

def cleanNumber(val):
    return val.replace('$', '').replace(' ', '').replace('.', '').replace(',', '.')

def getTaxeUniques(month):
    now = date.today()
    month_id = 'mes_'+month.lower()
    url = f'https://www.sii.cl/valores_y_fechas/impuesto_2da_categoria/impuesto{now.year}.htm'

    res = requests.get(url)

    if res.status_code == 200:
        soup = BeautifulSoup(res.content, 'html.parser')
        div_month = soup.find(id=month_id)
        taxes = []
        if div_month != None:
            tr = div_month.find('tbody').find_all('tr')
            for row in tr:
                if 'QUINCENAL' in row.text:
                    break
                if 'MENSUAL' in row.text:
                    continue
                taxeValue = {}
                contador = 0
                for val in row.find_all('td'):
                    if val.text:
                        contador += 1
                        if contador == 1:
                            taxeValue['from'] = float(cleanNumber(val.text))
                        if contador == 2:
                            if 'Y' in val.text:
                                taxeValue['to'] = 0
                            else:
                                taxeValue['to'] = float(cleanNumber(val.text))
                        if contador == 3:
                            taxeValue['factor'] = float(cleanNumber(val.text))
                        if contador == 4:
                            taxeValue['discount'] = float(cleanNumber(val.text))
                taxes.append(taxeValue)
        return taxes
    else:
        raise models.ValidationError(f'Error {res.status_code} Problema al comunicarse con SII')