from odoo.http import request


def send_notification(subject, body, author_id, user_group, model, model_id):
    partner_list = [
        usr.partner_id.id for usr in user_group if usr.partner_id
    ]
    mail_message = request.env['mail.message'].sudo().create({
        'subject': subject,
        'author_id': author_id,
        'body': body,
        'partner_ids': partner_list,
        'message_type': 'notification',
        'model': model,
        'res_id': model_id,
    })

    for user in user_group:
        request.env['mail.notification'].sudo().create({
            'mail_message_id': mail_message.id,
            'res_partner_id': user.partner_id.id,
            'notification_type': user.notification_type,
            'notification_status': 'ready'
        })


def get_followers(model_name, record_id):
    followers = request.env[model_name].sudo().search([('id', '=', record_id)]).message_follower_ids
    list_followers = []
    for follower in followers:
        user = request.env['res.users'].sudo().search([('partner_id', '=', follower.partner_id.id)])
        if user:
            list_followers.append(user)
    return list_followers
