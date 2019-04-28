from phase import *

# Game Properties =================================================================================

""" Game properties class. Handles year and phase. """
# Should handle things like game started, game finished, draw, etc.

class Game_Properties():
    game_properties = ""
    def __init__(self, year, phase):
        Game_Properties.game_properties = self
        self.phase = phase
        self.year = year
        
    def end_phase(self):
        self.phase = self.phase.end_phase()
        if isinstance(self.phase, Spring_Order_Phase):
            setattr(self, "year", self.year + 1)
        
    def __repr__(self):
        return "{}, {}".format(self.phase.name, self.year) 
        
    def __str__(self):
        return "Game Started: Phase: {}, Year: {}".format(self.phase.name, self.year)
        