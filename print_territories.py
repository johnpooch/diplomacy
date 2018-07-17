from dependencies import *

for k, v in territories.items(): 

    print("{{'{1}': '{0}'}},".format(k, v["display_name"]))