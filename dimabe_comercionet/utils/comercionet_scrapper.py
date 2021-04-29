import requests
from bs4 import BeautifulSoup
from pydifact.message import Message
from .edi_comercionet import create_sale_order_by_edi

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'

def download_documents(docs, s, doc_type='SRCU'):
    if docs:
        sales = []
        for doc in docs:
            try:
                res = s.get(
                    f"https://www.comercionet.cl/descargar_documentoAction.php?tipo=recibidos&docu_id={doc['id']}&formato={doc_type}")
                if res.status_code == 200:
                    sale = create_sale_order_by_edi(res.content.decode('unicode_escape'))
                    if sale:
                        sale['doc_id'] = doc['id']
                        sale['doc'] = res.content
                        sales.append(sale)
            except:
                continue
        return sales


def get_sale_orders():
    sale_orders = []
    s = requests.session()
    s.verify = False
    login_data = {
        'login': '7808800014004',
        'password': 'Alimpsaexcell2021'
    }
    s.post('https://www.comercionet.cl/usuarios/login.php', data=login_data)

    documents = []
    url = 'https://www.comercionet.cl/listadoDocumentos.php?tido_id=3&tipo=recibidos&entrada=1&offset='
    page = 0;
    get_row = True
    while get_row:
        res = s.get(url+str(page))
        last_document = documents[-1] if len(documents) > 0 else None
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            # buscar los documentos dentro de la tabla y guardarlos en una lista
            table_content = soup.find('table', {'class', 'tabla'}).find_all('tr')
            if table_content and len(table_content) > 0:
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
            else:
                get_row = False
        if documents[-1] == last_document:
            get_row = False
        page += 10
        
    if documents:
        sale_orders = download_documents(documents, s)

    return sale_orders