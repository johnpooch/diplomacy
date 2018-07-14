import bcrypt

players = [
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