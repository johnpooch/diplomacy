.PHONY: all

all: reset_db dev_fixtures superuser

dev_fixtures: dev_fixtures_basic dev_fixtures_games create_retreating_game \
	create_build_game create_orders_game create_long_game

dev_fixtures_basic:
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py loaddata \
		fixtures/dev/user.json \
		fixtures/dev/variant.json \
		fixtures/dev/nation.json \
		fixtures/dev/territory.json \
		fixtures/dev/named_coast.json \
		fixtures/dev/map_data.json \
		fixtures/dev/territory_map_data.json \
		fixtures/dev/named_coast_map_data.json 

dev_fixtures_games:
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py loaddata \
		fixtures/dev/games/game_1/game.json \
		fixtures/dev/games/game_1/pieces.json \
		fixtures/dev/games/game_1/turns/01_1900_spring_order/turn.json \
		fixtures/dev/games/game_1/turns/01_1900_spring_order/piece_states.json \
		fixtures/dev/games/game_1/turns/01_1900_spring_order/territory_states.json \
		fixtures/dev/games/game_2/game.json \
		fixtures/dev/games/game_2/pieces.json \
		fixtures/dev/games/game_2/turns/01_1900_spring_order/turn.json \
		fixtures/dev/games/game_2/turns/01_1900_spring_order/piece_states.json \
		fixtures/dev/games/game_2/turns/01_1900_spring_order/territory_states.json \
		fixtures/dev/games/game_2/turns/01_1900_spring_order/orders.json \
		fixtures/dev/games/game_2/turns/02_1900_fall_order/turn.json \
		fixtures/dev/games/game_2/turns/02_1900_fall_order/piece_states.json \
		fixtures/dev/games/game_2/turns/02_1900_fall_order/territory_states.json \
		fixtures/dev/games/game_3/game.json

create_orders_game:
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py convert_order_histories_to_data \
		order_histories/game_1/ --num_turns 1 --name 'Orders Game'

create_retreating_game:
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py convert_order_histories_to_data \
		order_histories/game_1/ --num_turns 2 --name 'Retreating Game'

create_build_game:
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py convert_order_histories_to_data \
		order_histories/game_1/ --num_turns 3 --name 'Build Game'

create_long_game:
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py convert_order_histories_to_data \
		order_histories/game_1/ --num_turns 14 --name 'Long Game'

reset_db:
	docker rm -vf diplomacy_diplomacy.mysql_1
	docker-compose up -d diplomacy.mysql
	docker exec -it diplomacy_diplomacy.service_1 .docker/deploy/wait-for-it.sh \
		diplomacy.mysql:3306 --timeout=60 -- echo "Diplomacy DB is up."
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py migrate

superuser:
	docker exec -it diplomacy_diplomacy.service_1 \
		./manage.py shell -c "from django.contrib.auth.models import User; \
		User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

create_game_from_history:
	docker exec -it diplomacy_diplomacy.service_1 \
		./manage.py convert_order_histories_to_data order_histories/game_1/ --num_turns 15
