.PHONY: all

all: reset_db dev_fixtures superuser

dev_fixtures: dev_fixtures_basic create_games

dev_fixtures_basic:
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py loaddata \
		cp_fixtures/dev/user.json \
		cp_fixtures/dev/variant.json \
		cp_fixtures/dev/nation.json \
		cp_fixtures/dev/territory.json \
		cp_fixtures/dev/named_coast.json \
		cp_fixtures/dev/map_data.json \
		cp_fixtures/dev/territory_map_data.json \
		cp_fixtures/dev/named_coast_map_data.json 

create_games:
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py create_game_fixtures

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
