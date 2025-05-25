VENV_DIR = venv
APP_DIR = app
TEST_DIR = tests
DOCKER_IMAGE_NAME = dermascan-app
DOCKER_COMPOSE_FILE = docker-compose.yml
DOCKER_NETWORK = dermascan-network

.PHONY: install venv run run_docker build stop test clean help migrate

install:
	@echo "Instalando dependencias..."
	pip install -r requirements.txt

venv:
	@echo "Creando entorno virtual..."
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r requirements.txt

run:
	@echo "Iniciando aplicación local (requiere DB corriendo)..."
	uvicorn app.main:app --reload --port 8000

run_docker: build
	@echo "Iniciando aplicación en Docker..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) up

build:
	@echo "Construyendo imagen Docker..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) build

stop:
	@echo "Deteniendo contenedores y limpiando recursos..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) down -v --remove-orphans

test:
	@echo "Ejecutando pruebas..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) run web pytest $(TEST_DIR)

clean: stop
	@echo "Limpiando todo el entorno..."
	rm -rf $(VENV_DIR)
	docker system prune -a -f
	docker volume prune -f

migrate:
	@echo "Ejecutando migraciones de la base de datos..."
	docker-compose -f $(DOCKER_COMPOSE_FILE) exec web alembic upgrade head

help:
	@echo "Comandos disponibles:"
	@echo "  make install       Instala las dependencias localmente"
	@echo "  make venv          Crea entorno virtual con dependencias"
	@echo "  make run           Inicia la aplicación en modo desarrollo local"
	@echo "  make run_docker    Inicia la aplicación en contenedores Docker"
	@echo "  make build         Reconstruye las imágenes Docker"
	@echo "  make stop          Detiene contenedores y limpia recursos Docker"
	@echo "  make test          Ejecuta las pruebas unitarias en Docker"
	@echo "  make clean         Limpieza completa (Docker y entorno local)"
	@echo "  make migrate       Ejecuta migraciones de base de datos"
	@echo "  make help          Muestra esta ayuda"
