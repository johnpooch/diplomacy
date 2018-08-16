from nation import *
from phase import *
from game_properties import *
from piece import *
from territory import *
from order import *
from werkzeug.security import generate_password_hash

# Nations -----------------------------------------------------------------------------------------

england = Nation("england", [], 3)
france = Nation("france", [], 3)
germany = Nation("germany", [], 3)
austria = Nation("austria", [], 3)
italy = Nation("italy", [], 3)
russia = Nation("russia", [], 4)
turkey = Nation("turkey", [], 3)
neutral = Neutral()

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
        
setattr(alb, 'shared_coasts', [gre, tri])
setattr(ank, 'shared_coasts', [arm, con])
setattr(apu, 'shared_coasts', [nap, ven])
setattr(arm, 'shared_coasts', [sev, ank])
setattr(ber, 'shared_coasts', [kie, pru])
setattr(bel, 'shared_coasts', [hol, pic])
setattr(bre, 'shared_coasts', [gas, pic])
setattr(cly, 'shared_coasts', [edi, lvp])
setattr(con, 'shared_coasts', [ank, smy])
setattr(den, 'shared_coasts', [kie, swe])
setattr(edi, 'shared_coasts', [cly, yor])
setattr(fin, 'shared_coasts', [swe])
setattr(gas, 'shared_coasts', [bre])
setattr(gre, 'shared_coasts', [alb, bul])
setattr(hol, 'shared_coasts', [bel, kie])
setattr(kie, 'shared_coasts', [ber, den, hol])
setattr(lon, 'shared_coasts', [wal, yor])
setattr(lvn, 'shared_coasts', [pru])
setattr(lvp, 'shared_coasts', [cly, wal])
setattr(mar, 'shared_coasts', [pie])
setattr(naf, 'shared_coasts', [tun])
setattr(nap, 'shared_coasts', [apu, rom])
setattr(nwy, 'shared_coasts', [swe])
setattr(pic, 'shared_coasts', [bre, bel])
setattr(pie, 'shared_coasts', [mar, tus])
setattr(por, 'shared_coasts', [])
setattr(rom, 'shared_coasts', [nap, tus])
setattr(rum, 'shared_coasts', [sev])
setattr(pru, 'shared_coasts', [ber, lvn])
setattr(sev, 'shared_coasts', [arm, rum])
setattr(smy, 'shared_coasts', [con, syr])
setattr(swe, 'shared_coasts', [den, fin, nwy])
setattr(syr, 'shared_coasts', [smy])
setattr(tri, 'shared_coasts', [alb, ven])
setattr(tun, 'shared_coasts', [naf])
setattr(tus, 'shared_coasts', [pie, rom])
setattr(ven, 'shared_coasts', [apu, tri])
setattr(wal, 'shared_coasts', [lon, lvp])
setattr(yor, 'shared_coasts', [edi, lon])
            
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

# Create intial pieces ----------------------------------------------------------------------------

# setattr(england, "pieces", [Army(lvp, england)])
# setattr(france, "pieces", [Army(par, france), Fleet(bre, france), Army(mar, france)])
# setattr(germany, "pieces", [Army(mun, germany), Fleet(kie, germany), Army(ber, germany)])
# setattr(austria, "pieces", [Army(bud, austria), Fleet(tri, austria), Army(vie, austria)])
# setattr(italy, "pieces", [Army(rom, italy), Fleet(nap, italy), Army(ven, italy)])
# setattr(russia, "pieces", [Army(mos, russia), Army(war, russia), Fleet(stp_sc, russia), Fleet(sev, russia)])
# setattr(turkey, "pieces", [Army(con, turkey), Army(smy, turkey), Fleet(ank, turkey)])

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

    
dummy_players = [
    {
        "username": "john",
        "email": "john@john.com",
        "password": generate_password_hash("abc"),
        "nation": "france",
        "orders_submitted" : 0, 
        "num_orders": 3, 
        "num_supply": 3, 
        "num_pieces": 3, 
    },
    {
        "username": "ross",
        "email": "ross@ross.com",
        "password": generate_password_hash("abc"), 
        "nation": "germany",
        "orders_submitted" : 0, 
        "num_orders": 3, 
        "num_supply": 3, 
        "num_pieces": 3, 
    },
    {
        "username": "hugh",
        "email": "hugh@hugh.com",
        "password": generate_password_hash("abc"), 
        "nation": "italy",
        "orders_submitted" : 0, 
        "num_orders": 3, 
        "num_supply": 3,
        "num_pieces": 3, 
    },
    {
        "username": "alex",
        "email": "alex@alex.com",
        "password": generate_password_hash("abc"),
        "nation": "england",
        "orders_submitted" : 0, 
        "num_orders": 3, 
        "num_supply": 3,
        "num_pieces": 3, 
    },
    {
        "username": "pearse",
        "email": "pearse@pearse.com",
        "password": generate_password_hash("abc"),
        "nation": "austria",
        "orders_submitted" : 0, 
        "num_orders": 3, 
        "num_supply": 3,
        "num_pieces": 3, 
    },
    {
        "username": "ollie",
        "email": "ollie@ollie.com",
        "password": generate_password_hash("abc"),
        "nation": "russia",
        "orders_submitted" : 0, 
        "num_orders": 4, 
        "num_supply": 4,
        "num_pieces": 4, 
    },
    {
        "username": "niall",
        "email": "niall@niall.com",
        "password": generate_password_hash("abc"),
        "nation": "turkey",
        "orders_submitted" : 0, 
        "num_orders": 3, 
        "num_supply": 3, 
        "num_pieces": 3, 
    },
]