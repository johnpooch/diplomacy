from dependencies import *

# get orders --------------------------------------------------------------------------------------

def get_orders():
    write_to_log("orders retrieved from database")
    return [order for order in mongo.db.orders.find()]
