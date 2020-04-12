load_dev_fixtures:
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py loaddata \
		fixtures/dev/user.json \
		fixtures/dev/variant.json \
		fixtures/dev/nation.json \
		fixtures/dev/territory.json \
		fixtures/dev/named_coast.json \
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



reset_db:
	docker rm -vf diplomacy_diplomacy.mysql_1
	docker-compose up -d diplomacy.mysql
	docker exec -it diplomacy_diplomacy.service_1 .docker/deploy/wait-for-it.sh \
		diplomacy.mysql:3306 --timeout=60 -- echo "Diplomacy DB is up."
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py migrate

