.PHONY: all

all: reset_db dev_fixtures superuser

dev_fixtures: create_games

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
