from main.models import Product

def clear_order(order):
    """Delete the order completely and return the products in case of an error. This is to help keep the data clean and everything aligned"""
    
    products = []
    
    for order_item in order.items.all():
        order_item.item.qty_available += order_item.qty
        products.append(order_item.item)
        order_item.delete_permanently()
        
    Product.objects.bulk_update(products, ["qty_available"])
    
    order.delete_permanently()
    
    return 