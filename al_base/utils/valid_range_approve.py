from odoo import models


def valid_range(values, range_ids):
    can_create = True
    range_affected = ''
    max_affected = 0
    min_affected = 0

    for item in range_ids:
        if 'min_amount' in values.keys() and 'max_amount' in values.keys():
            if item.max_amount != 0:
                if values['min_amount'] in range(item.min_amount, item.max_amount + 1) or values[
                    'max_amount'] in range(item.min_amount, item.max_amount + 1):
                    can_create = False
                    range_affected = item.name
                    max_affected = item.max_amount
                    min_affected = item.min_amount
                    break
            else:
                if values['min_amount'] >= item.min_amount:
                    can_create = False
                    range_affected = item.name
                    max_affected = item.max_amount
                    min_affected = item.min_amount
                    break


    if not can_create:
        if max_affected != 0:
            raise models.ValidationError(
                'No se puede guardar el registro con el rango entre {} y {}. Estos valores se encuentran dentro del {} entre {} y {}'.format(
                    values['min_amount'], values['max_amount'], range_affected, min_affected, max_affected))
        else:
            raise models.ValidationError(
                'No se puede guardar el registr con el rango entre {} y {}. Estos valores se encuentran dentro del {} entre {} y sin límite máximo'.format(
                    values['min_amount'], values['max_amount'], range_affected, min_affected))

    return can_create
