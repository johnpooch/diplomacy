load_all_fixtures:
	./manage.py loaddata \
		fixtures/game.json \
		fixtures/turn.json \
		fixtures/nations.json \
		fixtures/nation_states.json \
		fixtures/territories.json \
		fixtures/territory_states.json \
		fixtures/named_coasts.json \
		fixtures/supply_centers.json \
		fixtures/pieces.json
