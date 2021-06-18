from odoo import fields, models, api


class ChangeStateRouteLine(models.TransientModel):
    _name = 'change.state.route.line'

    line_id = fields.Many2one('route.map.line')

    state_id = fields.Many2one('ir.model.fields.selection', domain=[('field_id.model_id.name', '=', 'route.map.line'),
                                                                    ('value', '!=', 'to_delivered')])

    def change_state(self):
        for item in self:
            item.line_id.set_state(item.state_id.value)
