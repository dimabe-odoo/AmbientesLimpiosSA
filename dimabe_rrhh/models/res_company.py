from odoo import models,fields,api

class HrSalaryRule(models.Model):
    _inherit = 'res.company'

    analitic_account = fields.Selection([('1', 'Nómina'),('2', 'Contrato'),('3', 'Departamento')],'Origen Cuenta Analítica', help="Origen de Cuenta Analitica por Nómina, Contrato o Departamento, para Libro de Remuneraciones") 


    
