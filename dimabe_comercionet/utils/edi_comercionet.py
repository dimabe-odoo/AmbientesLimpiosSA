from pydifact.message import Message
from datetime import datetime
import pytz


def create_sale_order_by_edi(str_edi):
    try:
        message = Message.from_str(str_edi)

        sale_order = {}
        lines = []
        detail_line = {}

        for segment in message.segments:
            if segment.tag == 'BGM':
                sale_order['purchase_order'] = segment.elements[1]
            if segment.tag == 'DTM':
                if segment.elements[0][0] == '137':
                    sale_order['create_date'] = get_date_from_string(segment.elements[0][1])
                if segment.elements[0][0] == '2':
                    sale_order['dispatch_date'] = get_date_from_string(segment.elements[0][1])
                if segment.elements[0][0] == '43E':
                    sale_order['dispatch_date'] = get_date_from_string(segment.elements[0][1])
            if segment.tag == 'LOC':
                if type(segment.elements[1]) == list:
                    sale_order['client_code_comercionet'] = segment.elements[1][0]
                elif type(segment.elements[1]) == str:
                    sale_order['client_code_comercionet'] = segment.elements[1]
                else:
                    raise Exception('No es posible obtener el codigo del cliente')
            if segment.tag == 'NAD':
                if type(segment.elements[0]) == str and segment.elements[0].lower() == 'by':
                    sale_order['secondary_comercionet_box'] = segment.elements[1][0] if type(
                        segment.elements[1][0]) == str else ''
            if segment.tag == 'LIN':
                detail_line = {}
                discounts = []
                detail_line['number'] = int(segment.elements[0].split('.')[0])
                detail_line['product_code'] = segment.elements[2][0]
            if segment.tag == 'QTY':
                if segment.elements[0][0] == '21':
                    detail_line['quantity'] = int(segment.elements[0][1].split('.')[0])
            if segment.tag == 'MOA' and segment.elements[0][0] == '203':
                detail_line['final_price'] = int(segment.elements[0][1].split('.')[0])
            if segment.tag == 'PRI':
                detail_line['price'] = int(segment.elements[0][1].split('.')[0])
            if segment.tag == 'PCD':
                discount = {'percent': int(segment.elements[0][1].split('.')[0])}
            if segment.tag == 'MOA' and segment.elements[0][0] == '204':
                discount['amount'] = int(segment.elements[0][1].split('.')[0])
                discounts.append(discount)
                detail_line['discounts'] = discounts
            if detail_line and not any(d['number'] == detail_line['number'] for d in lines):
                lines.append(detail_line)
            if lines:
                sale_order['lines'] = lines

        line_number = 0
        for line in sale_order['lines']:
            line['discount_percent'] = (1 - (line['final_price'] / (line['quantity'] * line['price']))) * 100
            line_number = line['number']
        if sale_order['lines'] and len(sale_order['lines']) == line_number:
            return sale_order
        print('Las cantidades de lineas no son las mismas', sale_order['purchase_order'])
        return None
    except Exception as e:
        print(str_edi, e)
        return None


def get_date_from_string(string):
    year = string[0:4]
    month = string[4:6]
    day = string[6:8]
    date_return = datetime.strptime(f'{day}/{month}/{year}', "%d/%m/%Y").date()
    return date_return


