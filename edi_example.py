from pydifact.message import Message

str_edi = "UNB+UNOA:4+7807910CL0001:14+7808800014004:14+20210422:1110+20210422111011'UNH+001+ORDERS:D:01B:UN:EAN010'BGM+220+780791022074079547510+9'DTM+137:202104220000:102'DTM+2:202104280000:102'NAD+BY+7808810008659::EN'LOC+7+7808810010881'CTA+OC+:Alberto Urzua Prado'NAD+SU+7808800014004::EN'CTA+OC+:AMBIENTES LIMPIOS S.A.'CTA+OC+:AV. LA DIVISA 0363'CTA+OC+:2-8544944'PAT+1++21::D:60'TOD++NC'LIN+000001++17805020010059:SRV'IMD+F++CU:::ABRILLANT.PISOS FLOTANTES EXCELL 90'QTY+21:000000000000002:CS'QTY+45E:000000000000012:SIN'MOA+203:66449'PRI+AAA:43716::LIU::CS'ALC+A++++DE1'PCD+1:20'MOA+204:8743'ALC+A++++DE1'PCD+1:5'MOA+204:1749'LIN+000002++17805020001767:SRV'IMD+F++CU:::LIMP.PISOS EXCELL PORCELAN/PIEDRAS'QTY+21:000000000000001:CS'QTY+45E:000000000000012:SIN'MOA+203:21350'PRI+AAA:28092::LIU::CS'ALC+A++++DE1'PCD+1:20'MOA+204:5618'ALC+A++++DE1'PCD+1:5'MOA+204:1124'LIN+000003++17805020002344:SRV'IMD+F++CU:::LAVALOZAS EXCELL DOYPACK CON CLORO'QTY+21:000000000000001:CS'QTY+45E:000000000000008:SIN'MOA+203:6542'PRI+AAA:8607::LIU::CS'ALC+A++++DE1'PCD+1:20'MOA+204:1721'ALC+A++++DE1'PCD+1:5'MOA+204:344'UNS+S'MOA+86:94341'CNT+2:3'UNT+000053+001'UNZ+1+20210422111011'"


message = Message.from_str(str_edi)

sale_order = {}
lines = []
detail_line = {}

for segment in message.segments:
    if segment.tag == 'BGM': 
        sale_order['purchase_order'] = segment.elements[1]
    if segment.tag == 'LOC':
        sale_order['location'] = segment.elements[1]
    if segment.tag == 'LIN':
        detail_line = {}
        discounts = []
        detail_line['number'] = int(segment.elements[0])
        detail_line['sku'] = segment.elements[2][0]
    if segment.tag == 'QTY':
        if segment.elements[0] == '21':
            detail_line['quantity'] = int(segment.elements[1])
    if segment.tag == 'MOA' and segment.elements[0][0] == '203':
        detail_line['final_price'] =  segment.elements[0][1]
    if segment.tag == 'PRI':
        detail_line['price'] = segment.elements[0][1]
    if segment.tag == 'PCD':
        discount = {'percent': segment.elements[0][1]}
    if segment.tag == 'MOA' and segment.elements[0][0] == '204':
        discount['amount'] = segment.elements[0][1]
        discounts.append(discount)
        lines.append(detail_line)

print(sale_order, lines)

    

    