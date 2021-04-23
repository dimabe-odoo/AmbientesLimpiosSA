from pydifact.message import Message

def create_sale_order_by_edi(str_edi):
    message = Message.from_str(str_edi)

    sale_order = {}
    lines = []
    detail_line = {}

    for segment in message.segments:
        if segment.tag == 'BGM': 
            sale_order['purchase_order'] = segment.elements[1]
        if segment.tag == 'LOC':
            sale_order['client_code_comercionet'] = segment.elements[1]
        if segment.tag == 'LIN':
            detail_line = {}
            discounts = []
            detail_line['number'] = int(segment.elements[0])
            detail_line['product_code'] = segment.elements[2][0]
        if segment.tag == 'QTY':
            if segment.elements[0][0] == '21':
                detail_line['quantity'] = int(segment.elements[0][1])
        if segment.tag == 'MOA' and segment.elements[0][0] == '203':
            detail_line['final_price'] =  int(segment.elements[0][1])
        if segment.tag == 'PRI':
            detail_line['price'] = int(segment.elements[0][1])
        if segment.tag == 'PCD':
            discount = {'percent': int(segment.elements[0][1])}
        if segment.tag == 'MOA' and segment.elements[0][0] == '204':
            discount['amount'] = int(segment.elements[0][1])
            discounts.append(discount)
            detail_line['discounts'] = discounts
            if detail_line and not any(d['number'] == detail_line['number'] for d in lines):
                lines.append(detail_line)
        if lines:
            sale_order['lines'] = lines



    for line in sale_order['lines']:
        line['discount_percent'] = (1 - (line['final_price'] / (line['quantity'] * line['price']))) * 100

    return sale_order




    

    