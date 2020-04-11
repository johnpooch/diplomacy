load_dev_fixtures:
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py loaddata \
		fixtures/dev/user.json \
		fixtures/dev/variant.json \
		fixtures/dev/game.json \
		fixtures/dev/nation.json \
		fixtures/dev/territory.json \
		fixtures/dev/named_coast.json


reset_db:
	docker rm -vf diplomacy_diplomacy.mysql_1
	docker-compose up -d diplomacy.mysql
	docker exec -it diplomacy_diplomacy.service_1 .docker/deploy/wait-for-it.sh \
		diplomacy.mysql:3306 --timeout=60 -- echo "Diplomacy DB is up."
	docker exec -it diplomacy_diplomacy.service_1 ./manage.py migrate

