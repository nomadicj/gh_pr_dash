# Makefile

build:
	docker-compose build

run:
	docker-compose up

down:
	docker-compose down

test:
	docker-compose run --rm flask-app pytest

shell:
	docker-compose run --rm flask-app /bin/bash
