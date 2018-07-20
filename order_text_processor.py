from reps import reps, stp_reps

def replace_all(text, dic):
        for i, j in dic.items():
            text = text.replace(i, j)
        return text

def get_orders_from_txt(file):
    file = open(file, "r")
    order_list = []
    
    lines = file.read()
    lines = replace_all(lines, stp_reps)
    lines = replace_all(lines, reps)
    
    order_blocks = lines.split("\n\n")
    order_blocks = [block.split("\n") for block in order_blocks]
    
    print(order_blocks[0])
    phase = order_blocks[0][0]
    year = order_blocks[0][1]
    
    for block in order_blocks[1:]:
        nation = block[0].lower()
        
        for line in block[1:]:
            words = line.split(" ")
            
            # BUILD ===========================
            
            if block[0].lower() == "build":
                print("hello?")
                command = words[0].lower()
                if block[1].lower() == "army":
                    piece_type = "a"
                else:
                    piece_type = "f"
                target = words[2].lower()
                
                order = {
                    "nation": nation,
                    "origin": "",
                    "target": target,
                    "command": command,
                    "order_is_valid": True,
                    "object": "",
                    "phase": phase,
                    "year": year
                }
                print(order)
            
            # ===================================
            
            else: 
                target = ""
                _object = ""
                
                origin = words[0]
                command = words[1].lower()
                
                if words[1] == "MOVE":
                    target = words[2]
                
                if words[1] == "CONVOY" or words[1] == "SUPPORT":
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
                    "phase": phase,
                    "year": year,
                    "bounced": False,
                }
            order_list.append(order)
            
    return order_list