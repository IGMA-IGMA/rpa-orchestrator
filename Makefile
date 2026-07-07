.PHONY: help build up down restart logs shell test migrate makemigrations superuser health celery-worker celery-beat clean

help:
	@echo "Доступные команды:"
	@echo "  make build          - Собрать Docker образы"
	@echo "  make up             - Запустить все контейнеры"
	@echo "  make down           - Остановить все контейнеры"
	@echo "  make restart        - Перезапустить все контейнеры"
	@echo "  make logs           - Показать логи всех контейнеров"
	@echo "  make shell          - Открыть Django shell"
	@echo "  make test           - Запустить тесты"
	@echo "  make migrate        - Применить миграции"
	@echo "  make makemigrations - Создать миграции"
	@echo "  make superuser      - Создать суперпользователя"
	@echo "  make health         - Проверить health-check"
	@echo "  make celery-worker  - Запустить Celery worker отдельно"
	@echo "  make celery-beat    - Запустить Celery beat отдельно"
	@echo "  make clean          - Остановить всё и удалить тома"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

test:
	docker-compose exec web python manage.py test

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

superuser:
	docker-compose exec web python manage.py createsuperuser

health:
	curl -s http://localhost:8000/health/ | python -m json.tool

celery-worker:
	docker-compose exec celery-worker bash

celery-beat:
	docker-compose exec celery-beat bash

clean:
	docker-compose down -v

status:
	docker-compose ps
