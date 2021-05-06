import requests
import pdfkit
from odoo.tools.misc import find_in_path
from odoo import SUPERUSER_ID
from odoo import models
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import base64
import urllib.request
import codecs

def download_pdfs(documents):
    s = requests.session()
    login_data = {
            'login': '7808800014004',
            'password': 'Alimpsaexcell2021'
        }
    s.post('https://www.comercionet.cl/usuarios/login.php', data=login_data)
    result = []
    for doc in documents:
        url = "https://www.comercionet.cl/visualizacion/visualizar_documentoORDERS.php?tipo=recibidos&docu_id="+doc
        cookies = []
        for key, value in s.cookies.get_dict().items():
            cookies.append((key, value))
        options = {'cookie': cookies}
        pdfkit.from_html(url, "order.pdf", options=options)
        with open("order.pdf", "rb") as pdf_file:
            pdf_b64 = base64.b64encode(pdf_file.read())
        return None
        result.append({'doc_id': doc, 'pdf_file': pdf_b64})
    return result

