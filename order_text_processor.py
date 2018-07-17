from reps import reps

def replace_all(text, dic):
        for i, j in dic.items():
            text = text.replace(i, j)
        return text

def get_orders_from_txt(file):
    file = open(file, "r")
    order_list = []
    
    lines = file.read()
    lines = replace_all(lines, reps)
    
    order_blocks = lines.split("\n\n")
    order_blocks = [block.split("\n") for block in order_blocks]
    
    for block in order_blocks:
        nation = block[0].lower()
        
        for line in block[1:]:
            words = line.split(" ")
            
            target = ""
            _object = ""
            
            origin = words[0]
            command = words[1].lower()
            
            if words[1] == "MOVE":
                target = words[2]
            
            if words[2] == "CONVOY" or words[2] == "SUPPORT":
                _object = words[2]
                target = words[4]
            
            valid = (words[-1] == 'resolved')
        
            order = {
                "nation": nation,
                "origin": origin,
                "target": target,
                "command": command,
                "order_is_valid": valid,
                "object": _object,
                "phase": 0,
                "year": 1900
            }
            order_list.append(order)
    return order_list