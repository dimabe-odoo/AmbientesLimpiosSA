def get_range_amount(approve_purchase_ids, amount_total):
    approve_purchase_id = 0
    for item in approve_purchase_ids:
        if item.max_amount != 0:
            if item.min_amount <= amount_total <= item.max_amount:
                approve_purchase_id = item.id
                break
        else:
            if amount_total >= item.min_amount:
                approve_purchase_id = item.id
                break
    return approve_purchase_ids.filtered(lambda a: a.id == approve_purchase_id)


def get_range_discount(approve_sale_ids, amount_discount):
    approve_sale_id = 0
    for item in approve_sale_ids:
        if item.max_amount != 0:
            if item.min_amount <= amount_discount <= item.max_amount:
                approve_sale_id = item.id
                break
        else:
            if amount_discount >= item.min_amount:
                approve_sale_id = item.id
                break
    return approve_sale_ids.filtered(lambda a: a.id == approve_sale_id)



