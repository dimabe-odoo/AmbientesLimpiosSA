import requests
from bs4 import BeautifulSoup
from pydifact.message import Message
from .edi_comercionet import create_sale_order_by_edi
import urllib3


def download_documents(docs, s, doc_type='SRCU'):
    if docs:
        sales = []
        for doc in docs:
            try:
                res = s.get(
                    f"https://www.comercionet.cl/descargar_documentoAction.php?tipo=recibidos&docu_id={doc['id']}&formato={doc_type}")
                if res.status_code == 200:
                    sale = create_sale_order_by_edi(res.content.decode('utf-8'))
                    if sale:
                        sales.append(sale)
            except:
                continue
        return sales


def get_sale_orders():
    urllib3.disable_warnings()
    sale_orders = []
    s = requests.session()
    login_data = {
        'login': '7808800014004',
        'password': 'ptx123'
    }
    s.post('https://www.comercionet.cl/usuarios/login.php', data=login_data)

    res = s.get('https://www.comercionet.cl/listadoDocumentos.php?tido_id=3&tipo=recibidos&entrada=1')

    if res.status_code == 200:
        soup = BeautifulSoup(res.content, 'html.parser')

        documents = []

        # buscar los documentos dentro de la tabla y guardarlos en una lista
        table_content = soup.find('table', {'class', 'tabla'}).find_all('tr')
        for tr in table_content:
            td_counter = 0
            doc = {}
            for td in tr.find_all('td'):
                td_counter += 1
                if td_counter == 1:
                    try:
                        doc_id = td.find('input', {'class': 'radio'}).get('value')
                        doc['id'] = doc_id
                    except:
                        pass
                if td_counter == 7 and td.text:
                    doc['status'] = td.text
            if doc:
                documents.append(doc)

    if documents:
        sale_orders = download_documents(documents, s)

    return sale_orders