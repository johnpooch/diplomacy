import bcrypt

initial_pieces = [
    {
        "territory": "vie",
        "challenging": "vie",
        "owner": "austria",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "bud",
        "challenging": "bud",
        "owner": "austria",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "tri",
        "challenging": "tri",
        "owner": "austria",
        "piece_type": "f",
        "support": {},
		"convoyed_by": []
    },
    {
        # TESTING
        "territory": "lon",
        "challenging": "lon",
        "owner": "england",
        "piece_type": "f",
        "support": {},
		"convoyed_by": []
        
    },
    {
        # TESTING
        "territory": "nth",
        "challenging": "nth",
        "owner": "england",
        "piece_type": "f",
        "support": {},
		"convoyed_by": []
        
    },
    {
        # TESTING
        "territory": "yor",
        "challenging": "yor",
        "owner": "england",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "par",
        "challenging": "par",
        "owner": "france",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "mar",
        "challenging": "mar",
        "owner": "france",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "eng",
        "challenging": "eng",
        "owner": "france",
        "piece_type": "f",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "ber",
        "challenging": "ber",
        "owner": "germany",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "mun",
        "challenging": "mun",
        "owner": "germany",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "kie",
        "challenging": "kie",
        "owner": "germany",
        "piece_type": "f",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "rom",
        "challenging": "rom",
        "owner": "italy",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "ven",
        "challenging": "ven",
        "owner": "italy",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "nap",
        "challenging": "nap",
        "owner": "italy",
        "piece_type": "f",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "mos",
        "challenging": "mos",
        "owner": "russia",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "war",
        "challenging": "war",
        "owner": "russia",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "sev",
        "challenging": "sev",
        "owner": "russia",
        "piece_type": "f",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "stp",
        "challenging": "stp",
        "owner": "russia",
        "piece_type": "f",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "con",
        "challenging": "con",
        "owner": "turkey",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "ank",
        "challenging": "ank",
        "owner": "turkey",
        "piece_type": "f",
        "support": {},
		"convoyed_by": []
        
    },
    {
        "territory": "smy",
        "challenging": "smy",
        "owner": "turkey",
        "piece_type": "a",
        "support": {},
		"convoyed_by": []
        
    }
]
    
initial_ownership = {
    "ank": "turkey",
    "arm": "turkey",
    "bel": "neutral",
    "bre": "france",
    "bud": "austria",
    "bul": "neutral",
    "con": "turkey",
    "den": "neutral",
    "edi": "england",
    "gas": "france",
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
    "swe": "neutral",
    "tri": "austria",
    "tun": "neutral",
    "ven": "italy",
    "vie": "austria",
    "war": "russia"
}

initial_nations = [
    {
        "name": "france",
        "available": True
    },
    {
        "name": "germany",
        "available": True
    },
    {
        "name": "england",
        "available": True
    },
    {
        "name": "italy",
        "available": True
    },
    {
        "name": "austria",
        "available": True
    },
    {
        "name": "russia",
        "available": True
    },
    {
        "name": "turkey",
        "available": True
    }
]

initial_game_properties = {
    "game_started": False,
    "phase": 0,
    "year": 1901,
}
dummy_players = [
    {
        "username": "player_1",
        "email": "p1@p.com",
        "password": bcrypt.hashpw("1".encode('utf-8'), bcrypt.gensalt()),
        "nation": "france",
        "orders_finalised": False
    },
    {
        "username": "player_2",
        "email": "p2@p.com",
        "password": bcrypt.hashpw("2".encode('utf-8'), bcrypt.gensalt()), 
        "nation": "germany",
        "orders_finalised": False
    },
    {
        "username": "player_3",
        "email": "p3@p.com",
        "password": bcrypt.hashpw("3".encode('utf-8'), bcrypt.gensalt()), 
        "nation": "italy",
        "orders_finalised": False
    },
    {
        "username": "player_4",
        "email": "p4@p.com",
        "password": bcrypt.hashpw("4".encode('utf-8'), bcrypt.gensalt()),
        "nation": "england",
        "orders_finalised": False
    },
    {
        "username": "player_5",
        "email": "p5@p.com",
        "password": bcrypt.hashpw("5".encode('utf-8'), bcrypt.gensalt()),
        "nation": "austria",
        "orders_finalised": False
    },
    {
        "username": "player_6",
        "email": "p6@p.com",
        "password": bcrypt.hashpw("6".encode('utf-8'), bcrypt.gensalt()),
        "nation": "russia",
        "orders_finalised": False
    },
    {
        "username": "player_7",
        "email": "p7@p.com",
        "password": bcrypt.hashpw("7".encode('utf-8'), bcrypt.gensalt()),
        "nation": "turkey",
        "orders_finalised": False
    },
]