from dependencies import *
from territories import territories
from process_orders import process_orders
from resolve_challenges import resolve_challenges
from get_pieces import get_pieces
from get_orders import get_orders

# END TURN ========================================================================================

# save orders to history

def save_orders_to_history():
    order_history = mongo.db.order_history
    for order in get_orders():
        order_history.insert(order)

# check for retreats ------------------------------------------------------------------------------
def check_for_retreats():
    if any(piece["must_retreat"] for piece in get_pieces()):
            increment_phase(1)
    else: 
        increment_phase(2)
    
# increment year ----------------------------------------------------------------------------------

def increment_year():
    new_year = (mongo.db.game_properties.find_one()["year"] + 1)
    write_to_log("year incremented. new year: {}".format(new_year))
    mongo.db.game_properties.update({}, {"$set": {"year": new_year}})
    
# increment phase ---------------------------------------------------------------------------------

def increment_phase(num):
    new_phase = ((mongo.db.game_properties.find_one()["phase"] + 1) % 7)
    mongo.db.game_properties.update({}, {"$set": {"phase": new_phase}})
    write_to_log("phase incremented. new phase: {}".format(new_phase))
    if new_phase == 0: 
        increment_year()
        
# unfinalise_users --------------------------------------------------------------------------------

def unfinalise_users():
    mongo.db.users.update({}, {"$set": {"orders_finalised": False}}, multi=True)
    write_to_log("user orders unfinalised")

# process ----------------------------------------------------------------------------------------

# RETURN_ARRAY EX: [False, "description or error"]

def end_turn():
    clear_log()
    unfinalise_users()
    process_orders(get_orders())
    resolve_challenges()
    check_for_retreats()
    
    save_orders_to_history()
    # mongo.db.orders.remove({})
    flash('Orders proccessed!', 'success')
    
    # A GET OTHER PIECES FUNCTION WOULD BE GOOD
