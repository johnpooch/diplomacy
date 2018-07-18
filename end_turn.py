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
    return any(piece["must_retreat"] for piece in get_pieces())
    
# check for builds --------------------------------------------------------------------------------
# NEED TO MAKE THIS
def check_for_builds():
    return True
    
# increment year ----------------------------------------------------------------------------------

def increment_year():
    new_year = (mongo.db.game_properties.find_one()["year"] + 1)
    write_to_log("year incremented. new year: {}".format(new_year))
    mongo.db.game_properties.update({}, {"$set": {"year": new_year}})
    
# increment phase ---------------------------------------------------------------------------------

def increment_phase(num):
    mongo.db.game_properties.update({}, {"$set": {"phase": num}})
    write_to_log("phase incremented. new phase: {}".format(new_phase))
    if new_phase == 0: 
        increment_year()
        
# unfinalise_users --------------------------------------------------------------------------------

def unfinalise_users():
    mongo.db.users.update({}, {"$set": {"orders_finalised": False}}, multi=True)
    write_to_log("user orders unfinalised")

# move to next phase ------------------------------------------------------------------------------

def move_to_next_phase(current_phase):
    
    # if spring moves
    if current_phase == 0:
        if check_for_retreats():
            update_phase = 1
        else: 
            update_phase = 2
            
    # if spring retreats
    if current_phase == 1:
        update_phase = 2
            
    # if fall moves
    if current_phase == 2:
        if check_for_retreats():
            update_phase = 3
        elif check_for_builds():
            update_phase = 4
            
    # if fall retreats
    if current_phase == 3:
        if check_for_builds:
            update_phase = 4
        else: 
            update_phase = 0
        
    # if fall retreats
    if current_phase == 4:
        increment_year()
        update_phase = 0
        
    write_to_log("\nphase updated from {0} to {1}.".format(current_phase, update_phase))
    mongo.db.game_properties.update_one({}, {"$set": {"phase": update_phase}})

# process ----------------------------------------------------------------------------------------

# RETURN_ARRAY EX: [False, "description or error"]

def end_turn():
    clear_log()
    
    current_phase = mongo.db.game_properties.find_one({})["phase"]
    current_year = mongo.db.game_properties.find_one({})["year"]
    write_to_log("current phase: {}".format(current_phase))
    write_to_log("current year: {}\n".format(current_year))
    
    unfinalise_users()
    process_orders(get_orders())
    resolve_challenges(get_orders())
    
    move_to_next_phase(current_phase)
    
    save_orders_to_history()
    # mongo.db.orders.remove({})
    flash('Orders proccessed!', 'success')
    
    # A GET OTHER PIECES FUNCTION WOULD BE GOOD
