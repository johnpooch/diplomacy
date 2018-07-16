from dependencies import *

# ANNOUNCEMENTS ===================================================================================

# Write to file -----------------------------------------------------------------------------------

def write_to_file(filename, data):
    with open(filename, "a") as file:
        file.writelines(data)

# add announcements -------------------------------------------------------------------------------

def add_announcements(username, announcement):
    announcement = "({}) {}: {}\n".format(datetime.now().strftime("%H:%M:%S"), username, announcement)
    write_to_file("data/announcements.txt", announcement)

# get announcements -------------------------------------------------------------------------------
    
def get_announcements():
    announcements_list = []
    with open("data/announcements.txt", "r") as announcements: 
        announcements_list = announcements.readlines()
    return announcements_list
