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
            x = line.split(" ")
            valid = (x[-1] == 'resolved')
        
            order = {
                "nation": nation,
                "origin": x[0].lower(),
                "target": x[2].lower(),
                "command": x[1].lower(),
                "order_is_valid": valid,
                "object": "",
                "phase": 0,
                "year": 1900
            }
            
            order_list.append(order)
    return order_list
get_orders_from_txt("order_example.txt")