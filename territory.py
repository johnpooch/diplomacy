class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)

class Territory():
    __metaclass__ = IterRegistry
    _registry = []
    def __init__(self, name, display_name, neighbours):
        self._registry.append(self)
        self.name = name
        self.display_name = display_name
        self.neighbours = neighbours

    def __repr__(self):
        return "{}, {}, {}".format(self.name, self.display_name, self.neighbours)
        
    def __str__(self):
        return "Name: {}\nDisplay Name: {}, Neighbours: {}\n".format(self.name, self.display_name, self.neighbours)
        
class Water(Territory):
    def __init__(self, name, display_name, neighbours):
        Territory.__init__(self, name, display_name, neighbours)
        
class Coastal(Territory):
    def __init__(self, name, display_name, neighbours, shared_coast, supply_center):
        Territory.__init__(self, name, display_name, neighbours)
        self.shared_coast = shared_coast
        self.supply_center = supply_center
        
class Inland(Territory):
    def __init__(self, name, display_name, neighbours, supply_center):
        Territory.__init__(self, name, display_name, neighbours)
        self.supply_center = supply_center
        
class Special_Inland(Inland):
    def __init__(self, name, display_name, neighbours, supply_center, coasts):
        Inland.__init__(self, name, display_name, neighbours, supply_center)
        self.coasts = coasts
        
class Special_Coastal(Water):
    def __init__(self, name, display_name, neighbours, parent_territory):
        Water.__init__(self, name, display_name, neighbours)
        self.parent_territory = parent_territory


# Water Territories -------------------------------------------------------------------------------

adr = Water("adr", "adriatic sea", ["alb", "apu", "ion", "tri", "ven"])
aeg = Water("aeg", "aegean sea", ["bla", "bul-int", "bul-sc", "con", "eas", "gre", "ion", "smy"])
bal = Water("bal", "baltic sea", ["ber", "bot", "den", "kie", "pru", "ska", "swe"])
bar = Water("bar", "barrents sea", ["nrg", "nwy", "stp-int", "stp-sc"])
bla = Water("bla", "black sea", ["ank", "arm", "bul-int", "bul-nc", "con", "rum", "sev"])
bot = Water("bot", "gulf of bothnia", ["bal", "fin", "lvn", "swe", "stp-int", "stp-int"])
eas = Water("eas", "eastern mediterranean sea", ["aeg", "smy", "syr"])
eng = Water("eng", "english channel", ["bel", "bre", "iri", "lon", "mid", "nth", "pic", "wal"])
gol = Water("gol", "gulf of lyon", ["mar", "pie", "spa-int", "spa-sc", "tus", "tyn", "wes"])
hel = Water("hel", "heligoland blight", ["den", "hol", "kie", "nth"])
ion = Water("ion", "ionian sea", ["aeg", "alb", "apu", "gre", "nap", "tun", "tyn"])
iri = Water("iri", "irish sea", ["eng", "lvp", "mid", "nat", "wal"])
mid = Water("mid", "mid-atlantic ocean", ["bre", "eng", "gas", "iri", "naf", "nat", "spa-int", "spa-nc", "spa-sc", "por", "wes"])
nat = Water("nat", "north atlantic", ["cly", "iri", "lvp", "mid", "nrg"])
nrg = Water("nrg", "norwegian sea", ["bar", "cly", "edi", "nat", "nwy", "nth"])
nth = Water("nth", "north sea", ["bel", "den", "edi", "eng", "hel", "hol", "lon", "nrg", "nwy", "ska", "yor"])
ska = Water("ska", "skagerrak", ["bal", "den", "nth", "nwy", "swe"])
tyn = Water("tyn", "tyrhennian sea", ["gol", "ion", "nap", "rom", "tun", "tus", "wes"])
wes = Water("tyn", "western mediterranean", ["gol", "mid", "naf", "spa", "spa_sc", "tun", "tyn"])


# Coastal Territories ----------------------------------------------------------------------------

alb = Coastal("alb", "albania", ["adr", "gre", "ion", "ser", "tri"], ["gre", "tri"], False)
ank = Coastal("ank", "ankara", ["arm", "bla", "con", "smy"], ["arm", "con"], "turkey")
apu = Coastal("apu", "apulia", ["adr", "ion", "nap", "rom", "ven"], ["nap", "ven"], False)
arm = Coastal("arm", "armenia", ["ank", "ank", "sev", "smy", "syr"], ["sev", "ank"], "turkey")
ber = Coastal("ber", "berlin", ["bal", "kie", "mun", "pru", "sil"], ["kie", "pru"], "germany")
bel = Coastal("bel", "belgium", ["bur", "eng", "hol", "pic", "ruh"], ["hol", "pic"], "neutral")
bre = Coastal("bre", "brest", ["eng", "gas", "mid", "par", "pic"], ["gas", "pic"], "france")
cly = Coastal("cly", "clyde", ["edi", "lvp", "iri", "nat", "nrg"], ["edi", "lvp"], False)
con = Coastal("con", "constantinople", ["aeg", "ank", "bla", "bul-int", "bul-sc", "bul-nc", "smy"], ["ank", "smy"], "turkey")
den = Coastal("den", "denmark", ["bal", "hel", "kie", "nth", "ska", "swe"], ["kie", "swe"], "neutral")
edi = Coastal("edi", "edinburgh", ["cly", "lvp", "nat", "nrg", "nth", "yor"], ["cly", "yor"], "england")
fin = Coastal("fin", "finland", ["bot", "nwy", "stp-int", "stp-sc", "swe"], ["swe"], "england")
gas = Coastal("gas", "gascony", ["bre", "bur", "mar", "mid", "par", "spa-int", "spa-nc"], ["bre"], "france")
gre = Coastal("gre", "greece", ["aeg", "alb", "bul", "ion", "ser"], ["alb", "bul"], "neutral")
hol = Coastal("hol", "holland", ["bel", "hel", "kie", "nth", "ruh"], ["bel", "kie"], "neutral")
kie = Coastal("kie", "kiel", ["bal", "ber", "den", "hel", "hol", "mun", "ruh"], ["ber", "den", "hol"], "germany")
lon = Coastal("lon", "london", ["eng", "nth", "wal", "yor"], ["wal", "yor"], "england")
lvn = Coastal("lvn", "livonia", ["bal", "bot", "mos", "pru", "stp-int", "stp-sc", "war"], ["pru"], False)
lvp = Coastal("lvp", "liverpool", ["cly", "edi", "iri", "nat", "wal", "yor"], ["cly", "wal"], "england")
mar = Coastal("mar", "marseilles", ["bur", "gas", "gol", "pie", "spa-int", "spa-sc"], ["pie"], "france")
naf = Coastal("naf", "north africa", ["mid", "tun", "wes"], ["tun"], "neutral")
nap = Coastal("nap", "naples", ["apu", "ion", "rom", "tyn"], ["apu", "rom"], "italy")
nwy = Coastal("nwy", "norway", ["bar", "fin", "nrg", "nth", "ska", "stp-int", "stp-nc",  "swe"], ["swe"], "netural")
pic = Coastal("pic", "picardy", ["bre", "bel", "bur", "eng", "par"], ["bre", "bel"], False)
pie = Coastal("pie", "piedmont", ["gol", "mar", "tus", "tyr", "ven"], ["mar", "tus"], False)
por = Coastal("por", "portugal", ["mid", "spa", "spa_nc", "spa_sc"], [], "neutral")
rom = Coastal("rom", "rome", ["apu", "nap", "tus", "tyn", "ven"], ["nap", "tus"], "italy")
rum = Coastal("rum", "rumania", ["bla", "bud", "bul", "bul_nc", "gal", "ser", "sev", "ukr"], ["sev"], "neutral")
pru = Coastal("pru", "prussia", ["bal", "ber", "lvn", "sil", "war"], ["ber", "lvn"], False)
sev = Coastal("sev", "sevastapol", ["arm", "bla", "mos", "rum", "ukr"], ["arm", "rum"], "russia")
smy = Coastal("smy", "smyrna", ["aeg", "arm", "ank", "con", "eas", "syr"], ["con", "syr"], "turkey")
swe = Coastal("swe", "sweden", ["bal", "bot", "den", "fin", "nwy", "ska"], ["fin", "nwy"], "neutral")
syr = Coastal("syr", "syria", ["arm", "eas", "smy"], ["smy"], False)
tri = Coastal("tri", "trieste", ["adr", "alb", "bud", "syr", "tyr", "ven", "vie"], ["alb", "ven"], "austria")
tun = Coastal("tun", "tunis", ["ion", "naf", "tyn", "wes"], ["naf"], "neutral")
tus = Coastal("tus", "tuscany", ["gol", "pie", "rom", "tyn", "ven"], ["pie", "rom"], False)
ven = Coastal("ven", "venice", ["adr", "apu", "rom", "pie", "tri", "tyn", "tyr"], ["apu", "tri"], "italy")
wal = Coastal("wal", "wales", ["eng", "iri", "lon", "lvp", "yor"], ["lon", "lvp"], "england")
yor = Coastal("yor", "york", ["edi", "lon", "lvp", "nth", "wal"], ["edi", "lon"], False)


# Inland Territories -----------------------------------------------------------------------------

boh = Inland("boh", "bohemia", ["gal", "mun", "sil", "tyr", "vie"], False)
bud = Inland("bud", "budapest", ["gal", "rum", "ser", "tri", "vie"], "austria")
bul = Inland("bul", "bulgaria", ["aeg", "bla", "con", "gre", "rum", "ser"], "neutral")
bur = Inland("bur", "burgundy", ["bre", "bel", "gas", "mar", "mun", "par", "pic", "ruh",], False),
gal = Inland("gal", "galicia", ["boh", "bud", "rum", "sil", "ukr", "vie", "war"], False),
mos = Inland("mos", "moscow", ["lvn", "rum", "sev", "stp-int", "ukr", "war"], "russia"),
mun = Inland("mun", "munich", ["ber", "boh", "bur", "kie", "sil", "ruh", "tyr"], "germany"),
par = Inland("par", "paris", ["bre", "bur", "gas", "pic", "sil", "ruh", "tyr"], "france"),
ruh = Inland("ruh", "ruhr", ["bre", "bur", "hol", "kie", "mun"], "germany")
ser = Inland("ser", "serbia", ["alb", "bud", "bul", "gre", "rum", "tri"], "neutral")
sil = Inland("sil", "silesia", ["ber", "boh", "gal", "mun", "war"], False)
stp = Inland("stp", "st. petersburg", ["fin", "lvn", "mos", "nwy"], "russia")
tyr = Inland("tyr", "tyrolia", ["boh", "mun", "tri", "ven", "vie"], False)
ukr = Inland("ukr", "ukraine", ["gal", "mos", "rum", "sev", "war"], False)
vie = Inland("vie", "vienna", ["boh", "bud", "gal", "tri", "tyr"], "italy")
war = Inland("war", "warsaw", ["gal", "lvn", "mos", "sil", "pru", "ukr"], "russia")


# Special Inland Territories ---------------------------------------------------------------------

bul = Special_Inland("bul", "bulgaria", ["aeg", "bla", "con", "gre", "rum", "ser"], "neutral", ["bul-nc", "bul-sc"])
spa = Special_Inland("spa", "spain", ["gas", "mar", "por"], "neutral", ["spa-nc", "spa-sc"])
stp = Special_Inland("stp", "st. petersburg", ["fin", "lvn", "mos", "nwy"], "russia", ["stp-nc", "stp-sc"])


# Special Coastal Territories --------------------------------------------------------------------

bul_nc = Special_Coastal("bul-nc", "bulgaria (north coast)", ["bal", "fin", "lvn", "swe", "stp-int", "stp-int"], "bul")
bul_sc = Special_Coastal("bul-sc", "bulgaria (north coast)", ["aeg", "con", "gre"], "bul")

spa_nc = Special_Coastal("spa-nc", "spain (north coast)", ["bal", "fin", "lvn", "swe", "stp-int", "stp-int"], "spa")
spa_sc = Special_Coastal("spa-sc", "spain (north coast)", ["aeg", "con", "gre"], "spa")

stp_sc = Special_Coastal("stp_sc", "st. petersburg (south coast)", ["bot", "fin", "lvn"], "stp")
stp_nc = Special_Coastal("stp_nc", "st. petersburg (north coast)", ["bar", "nwy"], "stp")

for territory in Territory:
    print("setattr({}, neighbours, {})".format(territory.name, territory.neighbours))