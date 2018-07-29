from reps import reps, stp_reps
from objects import *
from instances import *
from pprint import pprint

def piece_exists_in_territory_and_belongs_to_user(territory):
    for piece in Piece.all_pieces:
        if piece.territory == territory:
            return piece

def find_territory_by_name(name):
    for territory in Territory.all_territories:
        if territory.name == name:
            return territory
            
def find_nation_by_name(name):
    for nation in Nation.all_nations:
        if nation.name == name:
            return nation

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
    
    for block in order_blocks:
        nation = block[0].lower()
        
        for line in block[1:]:
            # print(line)
            words = line.split(" ")
            if words[0].lower() == "build":
                command = "build"
            else:
                command = words[1].lower()
                origin = find_territory_by_name(words[0])
        
            if command == "hold":
                order = Hold(nation, origin)
            if command == "convoy":
                order = Convoy(nation, origin, find_territory_by_name(words[2]), find_territory_by_name(words[4]))
            if command == "move":
                order = Move(nation, origin, find_territory_by_name(words[2]))
            if command == "support":
                if words[4] == "hold":
                    words[4] = words[2]
                order = Support(nation, origin, find_territory_by_name(words[2]), find_territory_by_name(words[4]))
            if command == "retreat":
                order = Retreat(nation, origin, find_territory_by_name(words[2]))
            if command == "destroy":
                order = Destroy(nation, origin)
            
            if command != "build":
                # print(order)
                piece = piece_exists_in_territory_and_belongs_to_user(find_territory_by_name(words[0]))
                if piece:
                    piece.order = order
    
            if command == "build":
                Build(find_nation_by_name(nation), words[1], find_territory_by_name(words[2]))