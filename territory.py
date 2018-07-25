class Territory():
    def __init__(self, name, display_name, neighbours):
        self.name = name
        self.display_name = display_name
        self.neighbours = neighbours

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.display_name, self.neighbours)
        
    def __str__(self):
        return "Name: {}\nDisplay Name: {}, Neighbours: {}\n".format(self.name, self.display_name, self.neighbours)
        
class Water(Territory):
    def __init__(self, name, display_name, neighbours, parent_territory):
        Territory.__init__(self, name, display_name, neighbours)
        self.parent_territory = parent_territory
        
class Coastal(Territory):
    def __init__(self, name, display_name, neighbours, shared_coast, supply_center):
        Territory.__init__(self, name, display_name, neighbours)
        self.shared_coast = shared_coast
        self.supply_center = supply_center
        
class Inland(Territory):
    def __init__(self, name, display_name, neighbours, supply_center, parent_territory):
        Territory.__init__(self, name, display_name, neighbours)
        self.supply_center = supply_center

territories = [
    Water("adr", "adriatic sea", ["alb", "apu", "ion", "tri", "ven"], False), 
    Water("aeg", "aegean sea", ["bla", "bul-int", "bul-sc", "con", "eas", "gre", "ion", "smy"], False),  
    Water("bal", "baltic sea", ["ber", "bot", "den", "kie", "pru", "ska", "swe"], False), 
    Water("bar", "barrents sea", ["nrg", "nry", "stp-int", "stp-sc"], False), 
    Water("bla", "black sea", ["ank", "arm", "bul-int", "bul-nc", "con", "rum", "sev"], False),
    Water("bot", "gulf of bothnia", ["bal", "fin", "lvn", "swe", "stp-int", "stp-int"], False),
    Water("eas", "eastern mediterranean sea", ["aeg", "smy", "syr"], False),
    Water("eng", "english channel", ["bel", "bre", "iri", "lon", "mid", "nth", "pic", "wal"], False),
    Water("gol", "gulf of lyon", ["mar", "pie", "spa-int", "spa-sc", "tus", "tyn", "wes"], False),
    Water("hel", "heligoland blight", ["den", "hol", "kie", "nth"], False),
    Water("ion", "ionian sea", ["aeg", "alb", "apu", "gre", "nap", "tun", "tyn"], False),
    Water("iri", "irish sea", ["eng", "lvp", "mid", "nat", "wal"], False),
    Water("mid", "mid-atlantic ocean", ["bre", "eng", "gas", "iri", "naf", "nat", "spa-int", "spa-nc", "spa-sc", "por", "wes"], False),
    
    Coastal("alb", "albania", ["adr", "gre", "ion", "ser", "tri"], ["gre", "tri"], False),
    Coastal("ank", "ankara", ["arm", "bla", "con", "smy"], ["arm", "con"], "turkey"),
    Coastal("apu", "apulia", ["adr", "ion", "nap", "rom", "ven"], ["nap", "ven"], False),
    Coastal("arm", "armenia", ["ank", "ank", "sev", "smy", "syr"], ["sev", "ank"], "turkey"),
    Coastal("ber", "berlin", ["bal", "kie", "mun", "pru", "sil"], ["kie", "pru"], "germany"),
    Coastal("bel", "belgium", ["bur", "eng", "hol", "pic", "ruh"], ["hol", "pic"], "neutral"),
    Coastal("bre", "brest", ["eng", "gas", "mid", "par", "pic"], ["gas", "pic"], "france"),
    Coastal("cly", "clyde", ["edi", "lvp", "iri", "nat", "nrg"], ["edi", "lvp"], False),
    Coastal("con", "constantinople", ["aeg", "ank", "bla", "bul-int", "bul-sc", "bul-nc", "smy"], ["ank", "smy"], "turkey"),
    Coastal("den", "denmark", ["bal", "hel", "kie", "nth", "ska", "swe"], ["kie", "swe"], "neutral"),
    Coastal("edi", "edinburgh", ["cly", "lvp", "nat", "nrg", "nth", "yor"], ["cly", "yor"], "england"),
    Coastal("fin", "finland", ["bot", "nwy", "stp-int", "stp-sc", "swe"], ["swe"], "england"),
    Coastal("gas", "gascony", ["bre", "bur", "mar", "mid", "par", "spa-int", "spa-nc"], ["bre"], "france"),
    Coastal("gre", "greece", ["aeg", "alb", "bul", "ion", "ser"], ["alb", "bul"], "neutral"),
    Coastal("hol", "holland", ["bel", "hel", "kie", "nth", "ruh"], ["bel", "kie"], "neutral"),
    Coastal("kie", "kiel", ["bal", "ber", "den", "hel", "hol", "mun", "ruh"], ["ber", "den", "hol"], "germany"),
    Coastal("lon", "london", ["eng", "nth", "wal", "yor"], ["wal", "yor"], "england"),
    Coastal("lvn", "livonia", ["bal", "bot", "mos", "pru", "stp-int", "stp-sc", "war"], ["pru"], False),
    Coastal("lvp", "liverpool", ["cly", "edi", "iri", "nat", "wal", "yor"], ["cly", "wal"], "england"),
    Coastal("mar", "marseilles", ["bur", "gas", "gol", "pie", "spa-int", "spa-sc"], ["pie"], "france"),

    Inland("boh", "bohemia", ["gal", "mun", "sil", "tyr", "vie"], False, False),
    Inland("bud", "budapest", ["gal", "rum", "ser", "tri", "vie"], "austria", False),
    Inland("bul-int", "bulgaria", ["aeg", "bla", "con", "gre", "rum", "ser"], "neutral", "bul"),
    Inland("bur", "burgundy", ["bre", "bel", "gas", "mar", "mun", "par", "pic", "ruh",], False, False), 
    Inland("gal", "galicia", ["boh", "bud", "rum", "sil", "ukr", "vie", "war"], False, False), 
    ]



print(territories)

mid = Water("eng", "english channel", ["nwy"], False)
bre = Coastal("bre", "brest", ["par"], ["pic"], False)


print(mid.name)
print(bre.shared_coast)