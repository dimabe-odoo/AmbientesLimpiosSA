from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    afp_id = fields.Many2one('custom.afp', 'AFP')

    apv_id = fields.Many2one('custom.benefits.rrhh', 'Institución APV')

    is_fonasa = fields.Boolean('Es Fonasa')

    isapre_id = fields.Many2one('custom.isapre', 'Isapre')

    simple_charge = fields.Integer('Carga Simple')

    maternal_charge = fields.Integer('Carga Materna')

    disability_charge = fields.Integer('Carga Invalidez')

    isapre_agreed_quotes_uf = fields.Float('Cotizacion Pactada')

    fun_number = fields.Integer('Numero FUN')

    own_account_isapre = fields.Boolean('Cuenta propia Isapre')

    supplementary_insurance_id = fields.Many2one('custom.data',string='Seguro Complementario')

    not_afp = fields.Boolean('No Cotiza AFP')

    not_afp_sis = fields.Boolean('No Cotiza AFP SIS')

    have_saving_ccaf = fields.Boolean('Tiene Ahorro CCAF')

    saving_ccaf = fields.Float('Ahorro CCAF')

    currency_supplementary_insurance_id = fields.Many2one('res.currency', 'Moneda', domain=[('id', 'in', (45, 171))])

    supplementary_insurance_agreed_quotes_uf = fields.Float('Cotizacion Pactada')

    currency_isapre_id = fields.Many2one('res.currency', 'Moneda', domain=[('id', 'in', (45, 171))])

    is_pensionary = fields.Boolean('Pensionado')

    type_id = fields.Many2one('custom.data', 'Tipo de Contrato', domain=[('code','in',(1,2,3,4))])

    type_pensionary = fields.Selection(
        [('old', 'Pensión de Vejez'), ('disability', 'Pensión de Invalidez'), ('survival', 'Pensión de Sobreviviencia'),
         ('no', 'No Pensionado')]
        , default='no', string='Tipo de Pensión')

    collation_amount = fields.Float('Asig. Colación')

    mobilization_amount = fields.Float('Asig. Movilización')

    viatic_amount = fields.Float('Asig. Viático')

    advance_salary_amount = fields.Float('Anticipo de Sueldo')

    legal_gratification = fields.Boolean('Gratificación Legal Manual')

    section_type_id = fields.Integer(compute="_compute_section_type")

    section_id = fields.Many2one('custom.data','Tramo',domain=[('code','in',('A','B','C','D'))])

    section_amount = fields.Float('Monto Máximo Tramo')

    supplementary_insurance_type_id = fields.Integer(compute="_compute_supplementary_insurance_type")

    apv_type_id = fields.Integer(compute="_compute_apv_type")

    apv_amount = fields.Float('Monto APV')

    apv_currency = fields.Selection([('uf', 'UF'), ('clp', 'Pesos')], string='Tipo de Moneda', default="uf")

    apv_payment_term = fields.Selection([('1', 'Directa'), ('2', 'Indirecta')], string='Forma de Pago', default="1")

    @api.onchange('is_fonasa')
    def onchange_is_fonasa(self):
        for item in self:
            if item.is_fonasa:
                item.isapre_id = self.env['custom.isapre'].search([('code','=','07')]).id
            else:
                item.isapre_id = self.env['custom.isapre'].search([('code','=','00')]).id

    @api.model
    def _compute_section_type(self):
        for item in self:
            item.section_type_id = self.env.ref('dimabe_rrhh.custom_data_initial_section').id
   
    @api.model
    def _compute_supplementary_insurance_type(self):
        for item in self:
            item.supplementary_insurance_type_id = self.env.ref('dimabe_rrhh.custom_data_initial_complementary').id

    @api.model
    def _compute_apv_type(self):
        for item in self:
            item.apv_type_id = self.env.ref('dimabe_rrhh.custom_data_initial_apv').id

    @api.onchange('section_id')
    def onchange_section(self):
        if self.section_id.name:
            if self.section_id.code == 'D':
                self.section_amount = 0
            else:
                section_amount = self.env['custom.indicators.data'].search([('name','=',self.section_id.name + ' - Monto')], order='id desc')[0]
                self.section_amount = section_amount.value

    @api.onchange('wage')
    def onchange_wage(self):
        if self.wage and self.section_type_id:
            sections = self.env['custom.data'].search([('data_type_id','=',self.section_type_id)])
            for section in sections:
                if section.code == 'D':
                    self.section_id = section.id
                    break
                else:
                    max_salary_section = self.env['custom.indicators.data'].search([('name','=',section.name + ' - Tope')], order='id desc')[0]
                    if max_salary_section and self.wage <= max_salary_section.value:
                        self.section_id = section.id
                        break
            


    

