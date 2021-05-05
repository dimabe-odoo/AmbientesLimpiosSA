import requests
import pdfkit
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import base64
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
        # verificar configuración de wkhtmltopdf en odoo sh
        config = pdfkit.configuration(wkhtmltopdf='/bin/wkhtmltopdf/')
        pdfkit.from_url(url, "order.pdf", options=options,configuration=config)
        with open("order.pdf", "rb") as pdf_file:
            pdf_b64 = base64.b64encode(pdf_file.read())

        result.append({'doc_id' : doc, 'pdf_file': pdf_b64})
    return result

