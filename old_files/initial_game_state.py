from nation import *
from phase import *
from game_properties import *
from piece import *
from territory import *
from order import *

""" This script creates the object instances that exist at the start of the game. Dictionaries for pieces, ownership, 
    game properties are here. They are uploaded to the mongo db when the game is initialised. """

# Nations -----------------------------------------------------------------------------------------

england = Nation("england", [], 3)
france = Nation("france", [], 3)
germany = Nation("germany", [], 3)
austria = Nation("austria-hungary", [], 3)
italy = Nation("italy", [], 3)
russia = Nation("russia", [], 4)
turkey = Nation("turkey", [], 3)

neutral = ""


def get_nations():
    nations = Nation.all_nations
    nation_dicts = []
    for i in range(len(nations)):
        nation_dicts.append({
            "model": "service.nation",
            "pk": i + 1,
            "fields": {
                "name": nations[i].name
            }
            })
    return nation_dicts

# Water Territories -------------------------------------------------------------------------------

adr = Water("adr", "adriatic sea", [])
aeg = Water("aeg", "aegean sea", [])
bal = Water("bal", "baltic sea", [])
bar = Water("bar", "barrents sea", [])
bla = Water("bla", "black sea", [])
bot = Water("bot", "gulf of bothnia", [])
eas = Water("eas", "eastern mediterranean", [])
eng = Water("eng", "english channel", [])
gol = Water("gol", "gulf of lyon", [])
hel = Water("hel", "heligoland blight", [])
ion = Water("ion", "ionian sea", [])
iri = Water("iri", "irish sea", [])
mid = Water("mid", "mid_atlantic ocean", [])
nat = Water("nat", "north atlantic", [])
nrg = Water("nrg", "norwegian sea", [])
nth = Water("nth", "north sea", [])
ska = Water("ska", "skagerrack", [])
tyn = Water("tyn", "tyrrhenian sea", [])
wes = Water("wes", "western mediterranean", [])

# Coastal Territories ----------------------------------------------------------------------------

alb = Coastal("alb", "albania", [], [], False)
ank = Coastal("ank", "ankara", [], [], turkey)
apu = Coastal("apu", "apulia", [], [], False)
arm = Coastal("arm", "armenia", [], [], False)
ber = Coastal("ber", "berlin", [], [], germany)
bel = Coastal("bel", "belgium", [], [], neutral)
bre = Coastal("bre", "brest", [], [], france)
cly = Coastal("cly", "clyde", [], [], False)
con = Coastal("con", "constantinople", [], [], turkey)
den = Coastal("den", "denmark", [], [], neutral)
edi = Coastal("edi", "edinburgh", [], [], england)
fin = Coastal("fin", "finland", [], [], False)
gas = Coastal("gas", "gascony", [], [], False)
gre = Coastal("gre", "greece", [], [], neutral)
hol = Coastal("hol", "holland", [], [], neutral)
kie = Coastal("kie", "kiel", [], [], germany)
lon = Coastal("lon", "london", [], [], england)
lvn = Coastal("lvn", "livonia", [], [], False)
lvp = Coastal("lvp", "liverpool", [], [], england)
mar = Coastal("mar", "marseilles", [], [], france)
naf = Coastal("naf", "north africa", [], [], neutral)
nap = Coastal("nap", "naples", [], [], italy)
nwy = Coastal("nwy", "norway", [], [], neutral)
pic = Coastal("pic", "picardy", [], [], False)
pie = Coastal("pie", "piedmont", [], [], False)
por = Coastal("por", "portugal", [], [], neutral)
rom = Coastal("rom", "rome", [], [], italy)
rum = Coastal("rum", "rumania", [], [], neutral)
pru = Coastal("pru", "prussia", [], [], False)
sev = Coastal("sev", "sevastapol", [], [], russia)
smy = Coastal("smy", "smyrna", [], [], turkey)
swe = Coastal("swe", "sweden", [], [], neutral)
syr = Coastal("syr", "syria", [], [], False)
tri = Coastal("tri", "trieste", [], [], austria)
tun = Coastal("tun", "tunis", [], [], neutral)
tus = Coastal("tus", "tuscany", [], [], False)
ven = Coastal("ven", "venice", [], [], italy)
wal = Coastal("wal", "wales", [], [], False)
yor = Coastal("yor", "yorkshire", [], [], False)

# Inland Territories -----------------------------------------------------------------------------

boh = Inland("boh", "bohemia", [], False)
bud = Inland("bud", "budapest", [], austria)
bur = Inland("bur", "burgundy", [], False)
gal = Inland("gal", "galicia", [], False)
mos = Inland("mos", "moscow", [], russia)
mun = Inland("mun", "munich", [], germany)
par = Inland("par", "paris", [], france)
ruh = Inland("ruh", "ruhr", [], False)
ser = Inland("ser", "serbia", [], neutral)
sil = Inland("sil", "silesia", [], False)
tyr = Inland("tyr", "tyrolia", [], False)
ukr = Inland("ukr", "ukraine", [], False)
vie = Inland("vie", "vienna", [], austria)
war = Inland("war", "warsaw", [], russia)

# Special Inland Territories ---------------------------------------------------------------------

bul = Special_Inland("bul", "bulgaria", [], neutral, ["bul_ec", "bul_sc"])
spa = Special_Inland("spa", "spain", [], neutral, ["spa_nc", "spa_sc"])
stp = Special_Inland("stp", "st. petersburg", [], russia, ["stp_nc", "stp_sc"])

# Special Coastal Territories --------------------------------------------------------------------

bul_ec = Special_Coastal("bul_ec", "bulgaria (north coast)", [], "bul")
bul_sc = Special_Coastal("bul_sc", "bulgaria (south coast)", [], "bul")
spa_nc = Special_Coastal("spa_nc", "spain (north coast)", [], "spa")
spa_sc = Special_Coastal("spa_sc", "spain (south coast)", [], "spa")
stp_sc = Special_Coastal("stp_sc", "st. petersburg (south coast)", [], "stp")
stp_nc = Special_Coastal("stp_nc", "st. petersburg (north coast)", [], "stp")

# Assign neighbours to territories ----------------------------------------------------------------

setattr(adr, 'neighbours', [alb, apu, ion, tri, ven])
setattr(aeg, 'neighbours', [bla, bul, bul_sc, con, eas, gre, ion, smy])
setattr(bal, 'neighbours', [ber, bot, den, kie, pru, swe])
setattr(bar, 'neighbours', [nrg, nwy, stp, stp_sc])
setattr(bla, 'neighbours', [ank, arm, bul, bul_ec, con, rum, sev])
setattr(bot, 'neighbours', [bal, fin, lvn, swe, stp, stp])
setattr(eas, 'neighbours', [aeg, smy, syr])
setattr(eng, 'neighbours', [bel, bre, iri, lon, mid, nth, pic, wal])
setattr(gol, 'neighbours', [mar, pie, spa, spa_sc, tus, tyn, wes])
setattr(hel, 'neighbours', [den, hol, kie, nth])
setattr(ion, 'neighbours', [aeg, adr, alb, apu, gre, nap, tun, tyn])
setattr(iri, 'neighbours', [eng, lvp, mid, nat, wal])
setattr(mid, 'neighbours', [bre, eng, gas, iri, naf, nat, spa, spa_nc, spa_sc, por, wes])
setattr(nat, 'neighbours', [cly, iri, lvp, mid, nrg])
setattr(nrg, 'neighbours', [bar, cly, edi, nat, nwy, nth])
setattr(nth, 'neighbours', [bel, den, edi, eng, hel, hol, lon, nrg, nwy, ska, yor])
setattr(ska, 'neighbours', [den, nth, nwy, swe])
setattr(tyn, 'neighbours', [gol, ion, nap, rom, tun, tus, wes])
setattr(wes, 'neighbours', [gol, mid, naf, spa, spa_sc, tun, tyn])

setattr(alb, 'neighbours', [adr, gre, ion, ser, tri])
setattr(ank, 'neighbours', [arm, bla, con, smy])
setattr(apu, 'neighbours', [adr, ion, nap, rom, ven])
setattr(arm, 'neighbours', [ank, ank, sev, smy, syr])
setattr(ber, 'neighbours', [bal, kie, mun, pru, sil])
setattr(bel, 'neighbours', [bur, eng, hol, pic, ruh])
setattr(bre, 'neighbours', [eng, gas, mid, par, pic])
setattr(cly, 'neighbours', [edi, lvp, iri, nat, nrg])
setattr(con, 'neighbours', [aeg, ank, bla, bul, bul_sc, bul_ec, smy])
setattr(den, 'neighbours', [bal, hel, kie, nth, ska, swe])
setattr(edi, 'neighbours', [cly, lvp, nat, nrg, nth, yor])
setattr(fin, 'neighbours', [bot, nwy, stp, stp_sc, swe])
setattr(gas, 'neighbours', [bre, bur, mar, mid, par, spa, spa_nc])
setattr(gre, 'neighbours', [aeg, alb, bul, bul_sc, ion, ser])
setattr(hol, 'neighbours', [bel, hel, kie, nth, ruh])
setattr(kie, 'neighbours', [bal, ber, den, hel, hol, mun, ruh])
setattr(lon, 'neighbours', [eng, nth, wal, yor])
setattr(lvn, 'neighbours', [bal, bot, mos, pru, stp, stp_sc, war])
setattr(lvp, 'neighbours', [cly, edi, iri, nat, wal, yor])
setattr(mar, 'neighbours', [bur, gas, gol, pie, spa, spa_sc])
setattr(naf, 'neighbours', [mid, tun, wes])
setattr(nap, 'neighbours', [apu, ion, rom, tyn])
setattr(nwy, 'neighbours', [bar, fin, nrg, nth, ska, stp, stp_nc, swe])
setattr(pic, 'neighbours', [bre, bel, bur, eng, par])
setattr(pie, 'neighbours', [gol, mar, tus, tyr, ven])
setattr(por, 'neighbours', [mid, spa, spa_nc, spa_sc])
setattr(rom, 'neighbours', [apu, nap, tus, tyn, ven])
setattr(rum, 'neighbours', [bla, bud, bul, bul_ec, gal, ser, sev, ukr])
setattr(pru, 'neighbours', [bal, ber, lvn, sil, war])
setattr(sev, 'neighbours', [arm, bla, mos, rum, ukr])
setattr(smy, 'neighbours', [aeg, arm, ank, con, eas, syr])
setattr(swe, 'neighbours', [bal, bot, den, fin, nwy, ska])
setattr(syr, 'neighbours', [arm, eas, smy])
setattr(tri, 'neighbours', [adr, alb, bud, syr, tyr, ven, vie])
setattr(tun, 'neighbours', [ion, naf, tyn, wes])
setattr(tus, 'neighbours', [gol, pie, rom, tyn, ven])
setattr(ven, 'neighbours', [adr, apu, rom, pie, tri, tyn, tyr])
setattr(wal, 'neighbours', [eng, iri, lon, lvp, yor])
setattr(yor, 'neighbours', [edi, lon, lvp, nth, wal])

setattr(boh, 'neighbours', [gal, mun, sil, tyr, vie])
setattr(bud, 'neighbours', [gal, rum, ser, tri, vie])
setattr(bul, 'neighbours', [aeg, bla, con, gre, rum, ser])
setattr(bur, 'neighbours', [bre, bel, gas, mar, mun, par, pic, ruh])
setattr(gal, 'neighbours', [boh, bud, rum, sil, ukr, vie, war])
setattr(mos, 'neighbours', [lvn, rum, sev, stp, ukr, war])
setattr(mun, 'neighbours', [ber, boh, bur, kie, sil, ruh, tyr])
setattr(par, 'neighbours', [bre, bur, gas, pic, sil, ruh, tyr])
setattr(ruh, 'neighbours', [bre, bur, hol, kie, mun])
setattr(ser, 'neighbours', [alb, bud, bul, gre, rum, tri])
setattr(sil, 'neighbours', [ber, boh, gal, mun, war])
setattr(stp, 'neighbours', [fin, lvn, mos, nwy])
setattr(tyr, 'neighbours', [boh, mun, tri, ven, vie])
setattr(ukr, 'neighbours', [gal, mos, rum, sev, war])
setattr(vie, 'neighbours', [boh, bud, gal, tri, tyr])
setattr(war, 'neighbours', [gal, lvn, mos, sil, pru, ukr])
setattr(bul, 'neighbours', [aeg, bla, con, gre, rum, ser])
setattr(spa, 'neighbours', [gas, mar, por])
setattr(stp, 'neighbours', [fin, lvn, mos, nwy])
setattr(bul_ec, 'neighbours', [bla, con, rum])
setattr(bul_sc, 'neighbours', [aeg, con, gre])
setattr(spa_sc, 'neighbours', [gol, mar, mid, por, wes])
setattr(spa_nc, 'neighbours', [gas, mid, por])
setattr(stp_sc, 'neighbours', [bot, fin, lvn])
setattr(stp_nc, 'neighbours', [bar, nwy])
        
# Assign shared coasts to territories ----------------------------------------------------------------
l = [ 
    (alb, 'shared_coasts', [gre, tri]),
    (ank, 'shared_coasts', [arm, con]),
    (apu, 'shared_coasts', [nap, ven]),
    (arm, 'shared_coasts', [sev, ank]),
    (ber, 'shared_coasts', [kie, pru]),
    (bel, 'shared_coasts', [hol, pic]),
    (bre, 'shared_coasts', [gas, pic]),
    (cly, 'shared_coasts', [edi, lvp]),
    (con, 'shared_coasts', [ank, smy]),
    (den, 'shared_coasts', [kie, swe]),
    (edi, 'shared_coasts', [cly, yor]),
    (fin, 'shared_coasts', [swe]),
    (gas, 'shared_coasts', [bre]),
    (gre, 'shared_coasts', [alb, bul]),
    (hol, 'shared_coasts', [bel, kie]),
    (kie, 'shared_coasts', [ber, den, hol]),
    (lon, 'shared_coasts', [wal, yor]),
    (lvn, 'shared_coasts', [pru]),
    (lvp, 'shared_coasts', [cly, wal]),
    (mar, 'shared_coasts', [pie]),
    (naf, 'shared_coasts', [tun]),
    (nap, 'shared_coasts', [apu, rom]),
    (nwy, 'shared_coasts', [swe]),
    (pic, 'shared_coasts', [bre, bel]),
    (pie, 'shared_coasts', [mar, tus]),
    (por, 'shared_coasts', []),
    (rom, 'shared_coasts', [nap, tus]),
    (rum, 'shared_coasts', [sev]),
    (pru, 'shared_coasts', [ber, lvn]),
    (sev, 'shared_coasts', [arm, rum]),
    (smy, 'shared_coasts', [con, syr]),
    (swe, 'shared_coasts', [den, fin, nwy]),
    (syr, 'shared_coasts', [smy]),
    (tri, 'shared_coasts', [alb, ven]),
    (tun, 'shared_coasts', [naf]),
    (tus, 'shared_coasts', [pie, rom]),
    (ven, 'shared_coasts', [apu, tri]),
    (wal, 'shared_coasts', [lon, lvp]),
    (yor, 'shared_coasts', [edi, lon])
]
            
# Assign special coasts to territories ------------------------------------------------------------
            
setattr(bul, 'coasts', [bul_ec, bul_sc])
setattr(spa, 'coasts', [spa_nc, spa_sc])
setattr(stp, 'coasts', [stp_nc, stp_sc])            
  
# Assign parent territory to territories ----------------------------------------------------------

setattr(bul_ec, 'parent_territory', bul)
setattr(bul_sc, 'parent_territory', bul)
setattr(spa_sc, 'parent_territory', spa)
setattr(spa_nc, 'parent_territory', spa)
setattr(stp_nc, 'parent_territory', stp)
setattr(stp_sc, 'parent_territory', stp)


def get_territories():
    territories = Territory.all_territories
    key_dict = {}
    territories_dicts = []
    for i in range(len(territories)):
        t = territories[i]
        territories_dicts.append({
            "model": "service.territory",
            "pk": i + 1,
            "fields": {
                "abbreviation": t.name,
                "display_name": t.display_name,
                "neighbours": [],
                "shared_coasts": [],
                }
            })

        if isinstance(t, Inland) or isinstance(t, Coastal):
            territories_dicts[i]["fields"]["type"] = "L"

        if isinstance(t, Water):
            territories_dicts[i]["fields"]["type"] = "S"
        
        key_dict[t.name] = i + 1

    for i in range(len(territories)):
        t = territories[i]
        for n in t.neighbours:
            territories_dicts[i]["fields"]["neighbours"].append(key_dict[n.name])
        for y in l:
            if t.name == y[0].name:
                for sc in y[2]:
                    territories_dicts[i]["fields"]["shared_coasts"].append(key_dict[sc.name])

    return territories_dicts




initial_ownership = {
    "ank": "turkey",
    "bel": "neutral",
    "bre": "france",
    "bud": "austria",
    "bul": "neutral",
    "con": "turkey",
    "den": "neutral",
    "edi": "england",
    "gre": "neutral",
    "hol": "neutral",
    "kie": "germany",
    "lon": "england",
    "lvp": "england",
    "mar": "france",
    "mun": "germany",
    "mos": "russia",
    "nap": "italy",
    "par": "france",
    "por": "neutral",
    "rom": "italy",
    "ruh": "germany",
    "rum": "neutral",
    "ser": "neutral",
    "sev": "russia",
    "smy": "turkey",
    "spa": "neutral",
    "swe": "neutral",
    "stp": "russia",
    "tri": "austria",
    "tun": "neutral",
    "ven": "italy",
    "vie": "austria",
    "war": "russia"
}

initial_pieces = [
    {
        "territory": "vie",
        "previous_territory": "vie",
        "nation": "austria",
        "piece_type": "army",
		"retreat": False
    },
    {
        "territory": "bud",
        "previous_territory": "bud",
        "nation": "austria",
        "piece_type": "army",
		"retreat": False
    },
    {
        "territory": "tri",
        "previous_territory": "tri",
        "nation": "austria",
        "piece_type": "fleet",
		"retreat": False
    },
    {
        "territory": "lon",
        "previous_territory": "lon",
        "nation": "england",
        "piece_type": "fleet",
		"retreat": False
    },
    {
        "territory": "edi",
        "previous_territory": "edi",
        "nation": "england",
        "piece_type": "fleet",
		"retreat": False
    },
    {
        # TESTING
        "territory": "lvp",
        "previous_territory": "lvp",
        "nation": "england",
        "piece_type": "army",
		"retreat": False
        
    },
    {
        "territory": "par",
        "previous_territory": "par",
        "nation": "france",
        "piece_type": "army",
		"retreat": False
        
    },
    {
        "territory": "mar",
        "previous_territory": "mar",
        "nation": "france",
        "piece_type": "army",
		"retreat": False
        
    },
    {
        "territory": "bre",
        "previous_territory": "bre",
        "nation": "france",
        "piece_type": "fleet",
		"retreat": False
        
    },
    {
        "territory": "ber",
        "previous_territory": "ber",
        "nation": "germany",
        "piece_type": "army",
		"retreat": False
        
    },
    {
        "territory": "mun",
        "previous_territory": "mun",
        "nation": "germany",
        "piece_type": "army",
		"retreat": False
        
    },
    {
        "territory": "kie",
        "previous_territory": "kie",
        "nation": "germany",
        "piece_type": "fleet",
		"retreat": False
        
    },
    {
        "territory": "rom",
        "previous_territory": "rom",
        "nation": "italy",
        "piece_type": "army",
		"retreat": False
        
    },
    {
        "territory": "ven",
        "previous_territory": "ven",
        "nation": "italy",
        "piece_type": "army",
		"retreat": False
        
    },
    {
        "territory": "nap",
        "previous_territory": "nap",
        "nation": "italy",
        "piece_type": "fleet",
		"retreat": False
        
    },
    {
        "territory": "mos",
        "previous_territory": "mos",
        "nation": "russia",
        "piece_type": "army",
		"retreat": False
        
    },
    {
        "territory": "war",
        "previous_territory": "war",
        "nation": "russia",
        "piece_type": "army",
		"retreat": False
        
    },
    {
        "territory": "sev",
        "previous_territory": "sev",
        "nation": "russia",
        "piece_type": "fleet",
		"retreat": False
        
    },
    {
        "territory": "stp_sc",
        "previous_territory": "stp_sc",
        "nation": "russia",
        "piece_type": "fleet",
		"retreat": False,
		"coast": "sc"
    },
    {
        "territory": "con",
        "previous_territory": "con",
        "nation": "turkey",
        "piece_type": "army",
		"retreat": False
        
    },
    {
        "territory": "ank",
        "previous_territory": "ank",
        "nation": "turkey",
        "piece_type": "fleet",
		"retreat": False
        
    },
    {
        "territory": "smy",
        "previous_territory": "smy",
        "nation": "turkey",
        "piece_type": "army",
		"retreat": False
        
    }
]

initial_game_properties = {
    "phase": "spring order phase",
    "year": 1901,
}

    
