from odoo import _,fields, models, api
from odoo.tools import xml_utils
import logging
_logger = logging.getLogger(__name__)

class L10nClEdiUtilMixin(models.AbstractModel):
    _inherit = 'l10n_cl.edi.util'

    def _xml_validator(self, xml_to_validate, validation_type, is_doc_type_voucher=False):
        res = super(L10nClEdiUtilMixin, self)._xml_validator(xml_to_validate, validation_type, is_doc_type_voucher)
        if res and validation_type == 'bol':
            validation_types = {
                'doc': 'DTE_v10.xsd',
                'env': 'EnvioDTE_v10.xsd',
                'bol': 'EnvioBOLETA_v11.xsd',
                'recep': 'Recibos_v10.xsd',
                'env_recep': 'EnvioRecibos_v10.xsd',
                'env_resp': 'RespuestaEnvioDTE_v10.xsd',
                'sig': 'xmldsignature_v10.xsd',
                'book': 'LibroCV_v10.xsd',
                'consu': 'ConsumoFolio_v10.xsd',
            }
            xsd_fname = validation_types[validation_type]
            try:
                return xml_utils._check_with_xsd(xml_to_validate, xsd_fname, self.env)
            except FileNotFoundError:
                _logger.warning(
                    _('The XSD validation files from SII has not been found, please run manually the cron: "Download XSD"'))
                return True
