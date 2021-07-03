from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _default_country(self):
        try:
            return self.env.user.company_id.country_id or False
        except:
            return False

    country_id = fields.Many2one(
        "res.country",
        default=_default_country)
    state_id = fields.Many2one(
        "res.country.state", 'Ubication',
        domain="[('country_id', '=', country_id), ('type', '=', 'normal'), ('id', '!=', id)]", readonly=True)
    real_city = fields.Char('City')

    @api.onchange('city_id', 'city', 'state_id')
    def _change_city_province(self):
        if self.country_id != self.env.ref('base.cl'):
            return
        if self.city_id.state_id.parent_id:
            self.state_id = self.city_id.state_id.parent_id
        if self.state_id == self.env.ref('base.state_cl_13'):
            self.real_city = 'Santiago'
        else:
            self.real_city = self.city = self.city_id.name
            self.city = self.city_id.name

    def action_change_city_province(self, partner):
        if partner.country_id != self.env.ref('base.cl'):
                return
        if partner.city_id.state_id.parent_id:
            partner.write({
                    'state_id': partner.city_id.state_id.parent_id
            })
        if partner.state_id == self.env.ref('base.state_cl_13'):
            partner.write({
                    'real_city': 'Santiago'
            })
        else:
            partner.write({
                'real_city': partner.city,
                'city': partner.city_id.name,
            })
        if partner.street:
            partner.geo_localize()

    def create(self, values):
        res = super(ResPartner, self).create(values)
        self.action_change_city_province(res)
        return res
