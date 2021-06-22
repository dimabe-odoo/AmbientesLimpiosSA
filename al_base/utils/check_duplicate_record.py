from odoo.http import request


def check_duplicate(value, field_name, name_to_message, model_name, method, id_record=None):
    if method == 'create':
        record = request.env[model_name].search([(field_name, '=', value)])
    else:
        record = request.env[model_name].search([(field_name, '=', value), ('id', '!=', id_record)])
    if record:
        return {'have_record': True,'message': f'Ya existe un registro con {name_to_message} {value}'}
    else:
        return {'have_record': False, 'message': ''}
