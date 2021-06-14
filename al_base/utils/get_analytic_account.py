from odoo.http import request

def _get_by_partner(partner_id):
    parent_id = partner_id.id
    if partner_id.parent_id:
        parent_id = partner_id.parent_id.id

    return request.env['account.analytic.account'].search([('partner_id.id', '=', parent_id)])