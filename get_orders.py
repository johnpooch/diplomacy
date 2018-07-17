from dependencies import *

# get orders --------------------------------------------------------------------------------------

def get_orders():
    return [order for order in mongo.db.orders.find()]
