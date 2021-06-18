from xmlrpc import client


def make_done(data, state, latitude, longitude, observations):
    url = 'http://192.168.100.88:8069'
    db_name = 'alsa_pu_5'
    user = 'admin'
    password = 'dimabe21'
    common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db_name, user, password, {})

    models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    models.execute_kw(db_name, uid, password, 'ir.attachment', 'create', [data])
    models.execute_kw(db_name, uid, password, 'route.map.line', 'write', [[data['res_id']], {
        'state': state,
        'latitude_delivery': latitude,
        'longitude_delivery': longitude,
        'driver_observations': observations
    }])
