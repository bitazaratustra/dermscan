# Variables
VENV_DIR = venv
APP_DIR = app
TEST_DIR = tests
DOCKER_IMAGE_NAME = medical_app
DOCKER_COMPOSE_FILE = docker-compose.yml



# Install dependencies
install:
	@echo "Instalando dependencias..."
	pip install -r requirements.txt

# Create virtual environment (if needed)
venv:
	@echo "Creando entorno virtual..."
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt

# Run application locally using uvicorn
run_app:
	@echo "Iniciando la aplicación localmente..."
	uvicorn app.main:app --reload

# Run application using Docker Compose
run_docker: build
	@echo "Iniciando la aplicación en Docker..."
	docker-compose up

# Build Docker image
build:
	@echo "Construyendo imagen Docker..."
	docker-compose build

# Stop Docker containers
stop:
	@echo "Deteniendo contenedores Docker..."
	docker-compose down

# Run tests
test:
	@echo "Ejecutando pruebas..."
	pytest $(TEST_DIR)

# Clean environment (remove virtualenv)
clean:
	@echo "Limpiando entorno virtual..."
	rm -rf $(VENV_DIR)

# Show help
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
