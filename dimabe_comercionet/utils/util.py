def get_price_list(product, client):
    price_list = 0
    client_id = client
    if client.parent_id:
        client_id = client.parent_id

    if client_id.property_product_pricelist:
        for line in client_id.property_product_pricelist.item_ids:
            if line.product_tmpl_id.id == product.product_tmpl_id.id:
                price_list = line.fixed_price
                break

    return price_list