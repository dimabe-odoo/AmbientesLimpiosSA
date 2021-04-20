from odoo import api, fields, models
import xlsxwriter
from datetime import datetime
import base64
from collections import Counter
import io
import csv
from dateutil import relativedelta
import time

class WizardHrPayslip(models.TransientModel):
    _name = "wizard.hr.payslip"
    _description = 'XLSX Report'

    indicator_id = fields.Many2one('custom.indicators', string="Indicador")

    company_id = fields.Many2one('res.partner', domain=lambda self: [
        ('id', 'in', self.env['hr.employee'].sudo().search([('active', '=', True)]).mapped('address_id').mapped('id'))])

    #month = fields.Selection(
    #    [('Enero', 'Enero'), ('Febrero', 'Febrero'), ('Marzo', 'Marzo'), ('Abril', 'Abril'), ('Mayo', 'Mayo'),
    #     ('Junio', 'Junio'), ('Julio', 'Julio'),
    #     ('Agosto', 'Agosto'), ('Septiembre', 'Septiembre'), ('Octubre', 'Octubre'), ('Noviembre', 'Noviembre'),
    #     ('Diciembre', 'Diciembre'), ], string="Mes")

    #years = fields.Integer(string="Años", default=int(datetime.now().year))
    date_from = fields.Date('Fecha Inicial', required=True, default=lambda self: time.strftime('%Y-%m-01'))
    date_to = fields.Date('Fecha Final', required=True, default=lambda self: str(
        datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])

    def generate_remuneration_book(self):
        file_name = 'temp'
        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet(self.company_id.name)
        number_format=workbook.add_format({'num_format': '#,###'})
        indicators = self.env['custom.indicators'].sudo().search([('id', '=', f'{self.indicator_id.id}')])
        if not indicators:
            raise models.ValidationError(f'No existen datos del mes de {self.indicator_id.name}')
        if indicators.state != 'done':
            raise models.ValidationError(
                f'Los indicadores provicionales del mes de {indicators.name} no se encuentran validados')
        row = 13
        col = 0

        #payslips = self.env['hr.payslip'].sudo().search(
        #    [('indicator_id', '=', indicators.id), ('state', 'in', ['done', 'draft']),('employee_id.address_id.id','=',self.company_id.id), ('name', 'not like', 'Devolución:')])

        payslips = self.env['hr.payslip'].sudo().search(
            [('indicator_id', '=', self.indicator_id.id),('state','=','verify')])

        totals = self.env['hr.payslip.line'].sudo().search([('slip_id', 'in', payslips.mapped('id'))]).filtered(
            lambda a: a.total > 0)

        totals_result = []
        payslips = totals.mapped('slip_id')
        bold_format = workbook.add_format({'bold': True})
        worksheet.write(0, 0, self.company_id.name,bold_format)
        # GIRO worksheet.write(1,0, 'PROCESO Y COMERCIALIZACION DE NUECES', bold_format)
        worksheet.write(2,0, self.company_id.street, bold_format)
        worksheet.write(3,0, self.company_id.city, bold_format)
        worksheet.write(4,0, self.company_id.country_id.name, bold_format)
        worksheet.write(5,0, self.company_id.vat, bold_format)
        worksheet.write(6,0, 'Fecha Informe : '+datetime.today().strftime('%d-%m-%Y'), bold_format)
        worksheet.write(7,0, self.indicator_id.month, bold_format)
        worksheet.write(8,0, 'Fichas : Todas', bold_format)
        worksheet.write(9,0, 'Área de Negocio : Todas las Áreas de Negocios', bold_format)
        worksheet.write(10,0, 'Centro de Costo : Todos los Centros de Costos', bold_format)
        worksheet.write(11,0, 'Total Trabajadores : '+ str(len(payslips)), bold_format)
        for pay in payslips:
            #rules = self.env['hr.salary.rule'].sudo().search([('id', 'in', totals.mapped('salary_rule_id').mapped('id'))],
            #                                          order='order_number')
            rules = self.env['hr.salary.rule'].sudo().search([('id', 'in', totals.mapped('salary_rule_id').mapped('id'))])
            col = 0

            worksheet.write(row, col, pay.employee_id.display_name)
            worksheet.write(12, 0, 'Nombre', bold_format)
            long_name = max(payslips.mapped('employee_id').mapped('display_name'), key=len)
            worksheet.set_column(row, col, len(long_name))
            col += 1
            worksheet.write(12, 1, 'Rut', bold_format)
            worksheet.write(row, col, pay.employee_id.identification_id)
            long_rut = max(payslips.mapped('employee_id').mapped('identification_id'), key=len)
            worksheet.set_column(row, col, len(long_rut))
            col += 1
            worksheet.write(12, 2, 'N° Centro de Costo', bold_format)
            if pay.account_analytic_id.code:
                worksheet.write(row, col, pay.account_analytic_id.code)
            elif pay.contract_id.department_id.analytic_account_id.code:
                worksheet.write(row, col, pay.contract_id.department_id.analytic_account_id.code)
            else:
                worksheet.write(row, col, '')
            # Cuenta Analitica Por Departamento long_const = max(payslips.mapped('contract_id').mapped('department_id').mapped('analytic_account_id').mapped('name'),key=len)
            long_const = max(payslips.mapped('contract_id').mapped('analytic_account_id').mapped('name'),key=len)
            worksheet.set_column(row, col, len(long_const))
            col += 1
            worksheet.write(12, 3, 'Centro de Costo:', bold_format)
            if pay.account_analytic_id:
                worksheet.write(row, col, pay.account_analytic_id.name)
            elif pay.contract_id.department_id.analytic_account_id:
                worksheet.write(row, col, pay.contract_id.department_id.analytic_account_id.name)
            else:
                worksheet.write(row, col, '')
            #long_const = max(payslips.mapped('contract_id').mapped('department_id').mapped('analytic_account_id').mapped('name'),key=len)
            long_const = max(payslips.mapped('contract_id').mapped('analytic_account_id').mapped('name'),key=len)
            worksheet.set_column(row, col, len(long_const))
            col += 1
            worksheet.write(12, 4, 'Dias Trabajados:', bold_format)
            worksheet.write(row, col, self.get_worked_days(pay))
            col += 1
            worksheet.write(12, col, 'Cant. Horas Extras', bold_format)
            worksheet.write(row, col, self.get_qty_extra_hours(payslip=pay))
            totals_result.append({col : self.get_qty_extra_hours(payslip=pay)})
            col += 1
            for rule in rules:
                if not rule.show_in_book:
                    continue
                if not totals.filtered(lambda a: a.salary_rule_id.id == rule.id):
                    continue
                if rule.code == 'HEX50':
                    worksheet.write(12, col, 'Valor Horas Extras', bold_format)
                    total_amount = self.env["hr.payslip.line"].sudo().search(
                        [("slip_id", "=", pay.id), ("salary_rule_id", "=", rule.id)]).total
                    worksheet.write(row, col, total_amount,number_format)
                    totals_result.append({col : total_amount})
                elif rule.code == 'HEXDE':
                    worksheet.write(12, col, 'Cant. Horas Descuentos', bold_format)
                    worksheet.write(row, col, self.get_qty_discount_hours(payslip=pay))
                    totals_result.append({col : self.get_qty_discount_hours(payslip=pay)})
                    col += 1
                    worksheet.write(12, col, 'Monto Horas Descuentos', bold_format)
                    total_amount = self.env["hr.payslip.line"].sudo().search(
                        [("slip_id", "=", pay.id), ("salary_rule_id", "=", rule.id)]).total
                    worksheet.write(row, col,total_amount,number_format)
                    totals_result.append({col : total_amount})
                else:
                    total_amount = self.env["hr.payslip.line"].sudo().search(
                        [("slip_id", "=", pay.id), ("salary_rule_id", "=", rule.id)]).total
                    worksheet.write(12, col, rule.name, bold_format)
                    worksheet.write(row, col,total_amount,number_format)
                    totals_result.append({col : total_amount})
                col += 1
            col = 0
            row += 1
        counter = Counter()
        for item in totals_result:
            counter.update(item)
        total_dict = dict(counter)
        worksheet.write(row, 0, 'Totales',bold_format)
        number_bold_format = workbook.add_format({'num_format': '#,###', 'bold': True})
        for k in total_dict:
            worksheet.write(row, k,total_dict[k],number_bold_format)
        col = 0
        row += 1
        workbook.close()
        with open(file_name, "rb") as file:
            file_base64 = base64.b64encode(file.read())

        file_name = 'Libro de Remuneraciones {}'.format(indicators.name)
        attachment_id = self.env['ir.attachment'].sudo().create({
            'name': file_name,
            'datas': file_base64
        })
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment_id.id, ),
            'target': 'current',
        }
        return action

    def action_generate_csv(self):
        employee_model = self.env['hr.employee']
        payslip_model = self.env['hr.payslip']
        payslip_line_model = self.env['hr.payslip.line']
        company_country = self.env.user.company_id.country_id
        sex_data = {'male': "M", 'female': "F",}
        output = io.StringIO()
        #_logger = logging.getLogger(__name__)

        writer = csv.writer(output, delimiter=';', quotechar="'", quoting=csv.QUOTE_NONE)

        payslip_recs = payslip_model.sudo().search([('date_from','=',self.date_from),('state','!=','cancel'),('state','!=','draft'),('employee_id.address_id','=',self.company_id.id)])

        date_start = self.date_from
        date_stop = self.date_to
        date_start_format = date_start.strftime("%m%Y")
        date_stop_format = date_stop.strftime("%m%Y")
        line_employee = []
        rut = ""
        rut_dv = ""
        rut_emp = ""
        rut_emp_dv = ""

        try:
            rut_emp, rut_emp_dv = self.env.user.company_id.vat.split("-")
            rut_emp = rut_emp.replace('.', '')
        except:
            pass

        for payslip in payslip_recs:
            payslip_line_recs = payslip_line_model.sudo().search([('slip_id', '=', payslip.id)])
            rut = ""
            rut_dv = ""
            rut, rut_dv = payslip.employee_id.identification_id.split("-")
            rut = rut.replace('.', '')
            line_employee = [
                #1 RUT SIN DIGITO NI PUNTOS NI GUION
                self._shorten_str(rut, 11),
                #2 DIGITO VERIFICADOR
                self._shorten_str(rut_dv, 1),
                #3 APELLIDO
                self._format_str(payslip.employee_id.last_name.upper(), 30) if payslip.employee_id.last_name else '',
                #4 SEGUNDO APELLIDO
                self._format_str(payslip.employee_id.mothers_name.upper(), 30) if payslip.employee_id.mothers_name else '',
                #5 NOMBRES
                "%s %s" % (self._format_str(payslip.employee_id.first_name.upper(), 15), self._format_str(payslip.employee_id.middle_name.upper(), 15) if payslip.employee_id.middle_name else ''),
                #6 SEXO
                sex_data.get(payslip.employee_id.gender, '') if payslip.employee_id.gender else '',
                #7 NACION
                self.get_nacionality(payslip.employee_id.country_id.id),
                #8 TIPO PAGO
                self.get_pay_method(payslip.employee_id),
                #9 PERIODO DESDE
                date_start_format,
                #10 PERIOD HASTA 
                date_stop_format,
                #11 REGIMEN
                self.get_provisional_regime(payslip.contract_id),
                #12 TIPO TRABAJADOR
                '0',
                #13 DIAS TRABAJADOS
                str(round(self.get_worked_days(payslip and payslip[0] or False))),
                #14 TIPO LINEA
                self.get_line_type(payslip and payslip[0] or False),
                #15 COD MOVI
                payslip.personal_movements,
                #16 FECHA DESDE MOVIMIENTO PERSONAL (Si declara mov. personal 1, 3, 4, 5, 6, 7, 8 y 11 Fecha Desde es obligatorio y debe estar dentro del periodo de remun)
                payslip.date_from.strftime("%d/%m/%Y") if payslip.personal_movements != '0' else '00/00/0000',
                #17 FECHA HASTA MOVIMIENTO PERSONAL 
                payslip.date_to.strftime("%d/%m/%Y") if payslip.personal_movements != '0' else '00/00/0000',
                #18 TRAMO FAM
                payslip.contract_id.section_id.name[6:7],
                #19 CARGAS SIMPLES
                payslip.contract_id.simple_charge,
                #20 CARGA MAT
                payslip.contract_id.maternal_charge,
                #21 CARBA INV
                payslip.contract_id.disability_charge,
                #22 ASIG FAMILIAR
                self.get_payslip_lines_value(payslip, 'ASIGFAM') if self.get_payslip_lines_value(payslip ,'ASIGFAM') else '0',
                #23 ASIG RETRO
                self.get_payslip_lines_value(payslip, 'ASFRETRO') if self.get_payslip_lines_value(payslip, 'ASFRETRO') else '0',
                #24 REINT CARGAS
                '0',
                #25 SUBSIDIO TRABAJADOR JOVEN
                'N',
                #26 AFP
                payslip.contract_id.afp_id.code if payslip.contract_id.afp_id.code else '00',
                #27 IMPO AFP
                str(round(float(self.get_taxable_afp(payslip and payslip[0] or False,
                                                                      self.get_payslip_lines_value(payslip, 'TOTIM'),
                                                                      self.get_payslip_lines_value(payslip,
                                                                                                     'IMPLIC'))))),
                #28 COT AFP
                str(round(float(self.get_payslip_lines_value(payslip, 'PREV')))),
                #29 APORTE SIS
                str(round(float(self.get_payslip_lines_value(payslip, 'SIS')))),
                #30 CUENTA DE AHORRO VOLUNTARIO AFP
                '0',
                # 31 Renta Imp. Sust.AFP
                '0',
                # 32 Tasa Pactada (Sustit.)
                '0',
                # 33 Aporte Indemn. (Sustit.)
                '0',
                # 34 N Periodos (Sustit.)
                '0',
                # 35 Periodo desde (Sustit.)
                '0',
                # 36 Periodo Hasta (Sustit.)
                '0',
                # 37 Puesto de Trabajo Pesado
                ' ',
                # 38 % Cotizacion Trabajo Pesado
                '0',
                # 39 Cotizacion Trabajo Pesado
                '0',
                #40 codigo INS APVI
                payslip.contract_id.apv_id.code if self.get_payslip_lines_value(payslip,'APV') != '0' else '0',
                #41 NUM CONTRATO APVI
                '0',
                #42 FORMA DE PAGO APVI
                payslip.contract_id.forma_pago_apv if self.get_payslip_lines_value(payslip,'APV') else '0',
                #43 COTIZACION APVI
                str(round(float(self.get_payslip_lines_value(payslip, 'APV')))) if str(round(float(self.get_payslip_lines_value(payslip, 'APV')))) else '0',
                #44 COTIZACION DEPOSITO CONV
                ' ',
                # 45 Codigo Institucion Autorizada APVC
                '0',
                # 46 Numero de Contrato APVC
                '0',
                # 47 Forma de Pago APVC
                '0',
                # 48 Cotizacion Trabajador APVC
                '0',
                # 49 Cotizacion Empleador APVC
                '0',
                # 50 RUT Afiliado Voluntario 9 (11)
                '0',
                # 51 DV Afiliado Voluntario
                ' ',
                # 52 Apellido Paterno VOLUNTARIO
                ' ',
                # 53 Apellido Materno VOLUNTARIO
                '',
                # 54 Nombres VOLUNTARIO
                ' ',
                #55 CODIGO MOVIMIENTO PERSONAL
                            # Código Glosa
                            # 0 Sin Movimiento en el Mes
                            # 1 Contratación a plazo indefinido
                            # 2 Retiro
                            # 3 Subsidios
                            # 4 Permiso Sin Goce de Sueldos
                            # 5 Incorporación en el Lugar de Trabajo
                            # 6 Accidentes del Trabajo
                            # 7 Contratación a plazo fijo
                            # 8 Cambio Contrato plazo fijo a plazo indefinido
                            # 11 Otros Movimientos (Ausentismos)
                            # 12 Reliquidación, Premio, Bono
                            # TODO LIQUIDACION
                '0',
                # 56 Fecha inicio movimiento personal (dia-mes-año)
                '0',
                # 57 Fecha fin movimiento personal (dia-mes-año)
                '0',
                # 58 Codigo de la AFP
                '0',
                # 59 Monto Capitalizacion Voluntaria
                '0',
                # 60 Monto Ahorro Voluntario
                '0',
                # 61 Numero de periodos de cotizacion
                '0',
                # 62 Codigo EX-Caja Regimen
                '0',
                # 63 Tasa Cotizacion Ex-Caja Prevision
                '0',
                #64 RENTA IMPONIBLE IPS
                self.verify_ips(self.get_payslip_lines_value(payslip, 'TOTIM'), payslip.indicator_id.mapped('data_ids').filtered(lambda a: 'Para afiliados al IPS (ex INP)' in a.name).value) if self.get_payslip_lines_value(payslip,'TOTIM') else '0',            
                #65 COTIZACION OBLIGATORIO IPS
                '0',
                #66 RENTA IMPONIBL DESAHUCIO
                '0',
                #67 CODIGO EX-CAJA REGIMEN DESHAUCIO
                '0',
                #68 TASA COTIZACION DESAHUCIO
                '0',
                #69 COTIZACION DESHAUCIO
                '0',
                #70 COTIZACION FONASA
                self.get_payslip_lines_value(payslip,'FONASA') if payslip.contract_id.is_fonasa is True else '0',
                #71 COTIZACION ACC. TRABAJO ISL
                str(round(float(self.get_payslip_lines_value(payslip, 'ISL')))) if self.get_payslip_lines_value(
                                 payslip, 'ISL') else '0',
                #72 BONIFICACION LEY 15386
                '0',
                #73 DESCUENTO POR CARGAS FAMILIARES EN IPS
                '0',
                #74 BONOS GOBIERNO
                '0',
                #75 CODIGO INSTITUCION DE SALUD
                payslip.contract_id.isapre_id.code if payslip.contract_id.is_fonasa is False else '07'
                #76 NUMERO DEL FUN
                '' if payslip.contract_id.is_fonasa is True else payslip.contract_id.fun_number if payslip.contract_id.fun_number else '',
                #77 RENTA IMPONIBLE ISAPRE
                '0' if payslip.contract_id.is_fonasa is True else self.get_taxable_health(
                                 payslip and payslip[0] or False, self.get_payslip_lines_value(payslip, 'TOTIM')),
                
                #78 MONEDA DEL PLAN PACTADO ISAPRE
                '1' if payslip.contract_id.currency_isapre_id.name == 'CLP' or payslip.contract_id.is_fonasa is True else '2',
                #79 COTIZACION PACTADA
                '0' if payslip.contract_id.is_fonasa is True else payslip.contract_id.isapre_agreed_quotes_uf,
                #80 COTIZACION OBLIGATORIA ISAPRE
                '0' if payslip.contract_id.is_fonasa is True else
                             str(round(float(self.get_payslip_lines_value(payslip, 'SALUD')))),
                #81 COTIZACION ADICIONAL VOLUNTARIA
                '0' if payslip.contract_id.is_fonasa is True else str(round(float(self.get_payslip_lines_value(payslip, 'ADISA')))),
                #82 MONTO GARANTIA EXPLICITA DE SALUD
                '0',
                #83 CODIGO CCAF
                payslip.indicator_id.ccaf_id.code if payslip.indicator_id.ccaf_id.code else '00',
                #84 RENTA IMPONIBLE CCAF
                self.verify_ccaf(self.get_payslip_lines_value(payslip, 'TOTIM'),payslip.indicator_id.mapped('data_ids').filtered(lambda a: 'AFP' in a.name and a.type=='4').value) if self.get_payslip_lines_value(payslip,'TOTIM') else "0",
                #85 CREDITOS PERSONALES CCAF 
                self.get_payslip_lines_value(payslip, 'PCCAF') if self.get_payslip_lines_value(payslip,'PCCAF') else '0',
                #86 DESCUENTO DENTAL CCAF
                '0',
                #87 DESCUENTOS POR LEASING
                self.get_payslip_lines_value(payslip, 'CCAF') if self.get_payslip_lines_value(payslip,'CCAF') else '0',
                #88 DESXCUENTOS POR SEGURO DE VIDA
                '0',
                #89 OTROS DESCUENTOS CCAF
                '0',
                #90 COTIZACION A CCAF DE NO AFILIADOS A ISAPRES
                self.get_payslip_lines_value(payslip, 'CAJACOMP') if self.get_payslip_lines_value(payslip, 'CAJACOMP') else '0',
                #91 DESCUENTOS CARGAS FAMILIARES CCAF
                '0',
                #92 Otros descuentos CCAF 1
                '0',
                #93 Otros descuentos CCAF 2
                '0',
                #94 Bonos Gobierno  CCAF 
                '0',
                #95 CODIGO SUCURSAL CCAF
                '0',
                #96 CODIGO MUTUALIDAD
                payslip.indicator_id.mutuality_id.code if payslip.indicator_id.has_mutuality is True and payslip.indicator_id.mutuality_id.code else "00",
                #97 RENTA IMPOBILE MUTUAL
                self.get_mutuality_taxable(payslip and payslip[0] or False, self.get_payslip_lines_value(payslip, 'TOTIM')),
                #98 COTIZACION ACCIDENTE DEL TRABAJO
                str(round(float(self.get_payslip_lines_value(payslip, 'MUT')))) if self.get_payslip_lines_value(payslip, 'MUT') else '0',
                #99 CODIGO DE SUCURSAL PAGO MUTUAL
                '0',
                #100 RENTA IMPONIBLE SEGUR CESANTIA
                self.get_taxable_unemployment_insurance(payslip and payslip[0] or False, self.get_payslip_lines_value(payslip, 'TOTIM'), self.get_payslip_lines_value(payslip, 'IMPLIC')),
                #101 APORTE TRABAJADOR SEGURO CESANTIA
                str(round(float(self.get_payslip_lines_value(payslip, 'SECE')))) if self.get_payslip_lines_value(payslip, 'SECE') else '0',
                #102 APORTE EMPLEADO SEGURO CESANTIA
                str(self.verify_quotation_afc(
                                 self.get_taxable_unemployment_insurance(payslip and payslip[0] or False,
                                                                    self.get_payslip_lines_value(payslip, 'TOTIM'),
                                                                    self.get_payslip_lines_value(payslip, 'IMPLIC')),
                                 payslip.indicator_id, payslip.contract_id)),
                #103 RUT PAGADORA SUBSIDIO
                '0',
                #104 dv pafador subsidio
                '',
                #105 centro de costo, sucursal, agencia
                '0'
            ]
            writer.writerow([str(l) for l in line_employee])
        
        file_name = "Previred_{}{}.txt".format(self.date_to,
                                               self.company_id.display_name.replace('.', ''))
        attachment_id = self.env['ir.attachment'].sudo().create({
            'name': file_name,
            'datas': base64.encodebytes(output.getvalue().encode())
        })

        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment_id.id, ),
            'target': 'self',
        }
        return action



    @api.model
    def get_worked_days(self, payslip):
        worked_days = 0
        if payslip:
            for line in payslip.worked_days_line_ids:
                if line.code == 'WORK100':
                    worked_days = line.number_of_days
        return worked_days

    @api.model
    def get_qty_extra_hours(self, payslip):
        worked_days = 0
        if payslip:
            for line in payslip.input_line_ids:
                if line.code == 'HEX50':
                    worked_days = line.amount
        return worked_days

    @api.model
    def get_qty_discount_hours(self, payslip):
        worked_days = 0
        if payslip:
            for line in payslip.input_line_ids:
                if line.code == 'HEXDE':
                    worked_days = line.amount
        return worked_days

    @api.model
    def _shorten_str(self, text, size=1):
        c = 0
        shorten_text = ""
        while c < size and c < len(text):
            shorten_text += text[c]
            c += 1
        return shorten_text

    @api.model
    def _format_str(self, text, size=1):
        c = 0
        formated_text = ""
        special_chars = [
            ['á', 'a'],
            ['é', 'e'],
            ['í', 'i'],
            ['ó', 'o'],
            ['ú', 'u'],
            ['ñ', 'n'],
            ['Á', 'A'],
            ['É', 'E'],
            ['Í', 'I'],
            ['Ó', 'O'],
            ['Ú', 'U'],
            ['Ñ', 'N']]

        while c < size and c < len(text):
            formated_text += text[c]
            c += 1
        for char in special_chars:
            try:
                formated_text = formated_text.replace(char[0], char[1])
            except:
                pass
        return formated_text

    @api.model
    def get_nacionality(self, country):
        if country == 46:
            return 0
        else:
            return 1
    @api.model
    def get_pay_method(self, employee):
        # 01 Remuneraciones del mes
        # 02 Gratificaciones
        # 03 Bono Ley de Modernizacion Empresas Publicas
        # TODO: en base a que se elije el tipo de pago???
        return 1

    @api.model 
    def get_provisional_regime(self, contract):
        if contract.is_pensionary is True:
            return 'SIP'
        else:
            return 'AFP'

    @api.model
    def get_line_type(self, payslip):
        # 00 Linea Principal o Base
        # 01 Linea Adicional
        # 02 Segundo Contrato
        # 03 Movimiento de Personal Afiliado Voluntario
        return '00'

    @api.model
    def get_payslip_lines_value(self, obj, rule):
        val = 0
        lines = self.env['hr.payslip.line']
        details = lines.search([('slip_id','=',obj.id),('code','=', rule)])
        val = round(details.total)
        return val

    @api.model
    def get_taxable_afp(self, payslip, TOTIM, LIC):
        LIC_2 = float(LIC)
        TOTIM_2 = float(TOTIM)
        if LIC_2 > 0:
            TOTIM = LIC
        if payslip.contract_id.is_pensionary is True:
            return '0.0'
        elif TOTIM_2 >= round(payslip.indicator_id.mapped('data_ids').filtered(lambda a: 'AFP' in a.name and a.type=='4').value):
            return str(round(float(payslip.indicator_id.mapped('data_ids').filtered(lambda a: 'AFP' in a.name and a.type=='4').value)))
        else:
            return str(round(float(round(TOTIM_2))))

    @api.model
    def verify_ips(self, TOTIM, TOPE):
        if float(TOTIM) > (TOPE):
            data = round(float(TOPE))
            return data
        else:
            return TOTIM

    @api.model
    def get_taxable_health(self, payslip, TOTIM):
        result = 0
        if float(TOTIM) >= round(payslip.indicator_id.mapped('data_ids').filtered(lambda a: 'AFP' in a.name and a.type=='4').value):
            return str(round(float(payslip.indicator_id.mapped('data_ids').filtered(lambda a: 'AFP' in a.name and a.type=='4').value)))
        else:
            return str(round(float(TOTIM)))
   
    @api.model
    def get_mutuality_taxable(self, payslip, TOTIM):
        if payslip.indicator_id.has_mutuality is False:
            return 0
        elif payslip.contract_id.type_id.code == 4: #SUELDO EMPRESARIAL
            return 0
        elif float(TOTIM) >= round(payslip.indicator_id.mapped('data_ids').filtered(lambda a: 'AFP' in a.name and a.type=='4').value):
            return round(payslip.indicator_id.mapped('data_ids').filtered(lambda a: 'AFP' in a.name and a.type=='4').value)
        else:
            return round(float(TOTIM))

    @api.model
    def get_taxable_unemployment_insurance(self, payslip, TOTIM, LIC):
        LIC_2 = float(LIC)
        TOTIM_2 = float(TOTIM)
        if TOTIM_2 < payslip.indicator_id.mapped('data_ids').filtered(lambda a: a.type == 5 and 'Trab. Dependientes e Independientes' in a.name).value:
            return 0
        if LIC_2 > 0:
            TOTIM = LIC
        if payslip.contract_id.is_pensionary is True:
            return 0
        elif payslip.contract_id.type_id.code == 4 :#'Sueldo Empresarial'
            return 0
        elif TOTIM_2 >= round(payslip.indicator_id.mapped('data_ids').filtered(lambda a: a.type == 4 and 'Para Seguro de Cesantía' in a.name).value):
            return str(round(
                float(round(payslip.indicator_id.mapped('data_ids').filtered(lambda a: a.type == 4 and 'Para Seguro de Cesantía' in a.name).value))))
        else:
            return str(round(float(round(TOTIM_2))))

    @api.model
    def verify_quotation_afc(self, TOTIM, indicator, contract):
        totimp = float(TOTIM)
        if contract.type_id.code == 2 :#Plazo Fijo
            return round(totimp * indicator.mapped('data_ids').filtered(lambda a: a.name == 'Contrato Plazo Fijo Empleador').percentage_value / 100)
        elif contract.type_id.code == 1: #Plazo Indefinido
            return round(totimp * indicator.mapped('data_ids').filtered(lambda a: a.name == 'Contrato Plazo Indefinido Empleador').percentage_value / 100)
        else:
            return 0

    @api.model
    def verify_ccaf(self, TOTIM, TOPE):
        if TOTIM:
            TOTIM_2 = float(TOTIM)
            if TOTIM_2 > (TOPE):
                data = round(float(TOPE))
                return str(data)
            else:
                return str(TOTIM)
        else:
            return "0"