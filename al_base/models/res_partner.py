from odoo import models, api, fields
from ..utils.rut_helper import RutHelper


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self,values):
        if isinstance(values,list):
            for val in values:
                if 'parent_id' in val.keys():
                    parent_id = self.env['res.partner'].search([('id','=',val['parent_id'])])
                    if parent_id.l10n_cl_dte_email and parent_id.l10n_cl_dte_email != '':
                        val['l10n_cl_dte_email'] = parent_id.l10n_cl_dte_email
                        val['l10n_cl_activity_description'] = parent_id.l10n_cl_activity_description
        else:
            if 'parent_id' in values.keys():
                parent_id = self.env['res.partner'].search([('id', '=', values['parent_id'])])
                if parent_id.l10n_cl_dte_email and parent_id.l10n_cl_dte_email != '':
                    values['l10n_cl_dte_email'] = parent_id.l10n_cl_dte_email
                    values['l10n_cl_activity_description'] = parent_id.l10n_cl_activity_description

        return super(ResPartner, self).create(values)
