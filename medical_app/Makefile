
VENV_DIR = venv
APP_DIR = app
TEST_DIR = tests
DOCKER_IMAGE_NAME = medical_app
DOCKER_COMPOSE_FILE = docker-compose.yml



install:
	@echo "Instalando dependencias..."
	pip install -r requirements.txt

venv:
	@echo "Creando entorno virtual..."
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt


run_app:
	@echo "Iniciando la aplicación localmente..."
	uvicorn app.main:app --reload


run_docker: build
	@echo "Iniciando la aplicación en Docker..."
	docker-compose up


build:
	@echo "Construyendo imagen Docker..."
	docker-compose build


stop:
	@echo "Deteniendo contenedores Docker..."
	docker-compose down


test:
	@echo "Ejecutando pruebas..."
	pytest $(TEST_DIR)


clean:
	@echo "Limpiando entorno virtual..."
	rm -rf $(VENV_DIR)

help:
	@echo "Comandos disponibles:"
	@echo "  make install       Instala las dependencias"
	@echo "  make venv          Crea el entorno virtual y instala dependencias"
	@echo "  make run           Ejecuta la aplicación usando Docker Compose"
	@echo "  make build         Construye la imagen Docker"
	@echo "  make stop          Detiene los contenedores Docker"
	@echo "  make test          Ejecuta las pruebas"
	@echo "  make clean         Limpia el entorno de Docker (contenedores, imágenes y volúmenes)"
	@echo "  make help          Muestra esta ayuda"
