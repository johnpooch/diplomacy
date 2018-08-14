from write_to_log import write_to_log
from phase import *

# Game Properties =================================================================================

class Game_Properties():
    game_properties = ""
    def __init__(self, year, phase):
        Game_Properties.game_properties = self
        self.phase = phase
        self.year = year
        
    def end_phase(self):
        self.phase = self.phase.end_phase()
        write_to_log("\nnew phase: {}.".format(self.phase.name))
        if isinstance(self.phase, Spring_Order_Phase):
            setattr(self, "year", self.year + 1)
            write_to_log("new year: {}.".format(self.year))
        
    def __repr__(self):
        
        return "{}, {}".format(self.phase.name, self.year) 
        
    def __str__(self):
        return "Game Started: Phase: {}, Year: {}".format(self.phase.name, self.year)
        