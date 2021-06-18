def get_price_list(product, client):
    client_id = client
    if client.parent_id:
        client_id = client.parent_id

    if client_id.property_product_pricelist:
        for line in client_id.property_product_pricelist.item_ids:
            if line.product_tmpl_id.id == product.product_tmpl_id.id:
                return line.fixed_price

    return False