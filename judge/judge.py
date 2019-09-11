def process(data):
    """
    Takes a single python dictionary representing the current game state and
    all orders.

    Returns a dict describing the outcomes for each command.
    """
    territories = data['territories']
    pieces = data['pieces']
