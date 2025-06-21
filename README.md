# DermScan - Sistema de Diagnóstico Dermatológico Avanzado

![DermScan Architecture](https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.pngwing.com%2Fes%2Fsearch%3Fq%3Ds%25C3%25ADmbolo%2Bm%25C3%25A9dico&psig=AOvVaw1_IwXcZotPvZB7xyu15PTU&ust=1750599882164000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCKC4gIzTgo4DFQAAAAAdAAAAABAE) 

Aplicación web para diagnóstico asistido de enfermedades dermatológicas mediante deep learning. Permite a usuarios subir imágenes de lesiones cutáneas y recibe análisis predictivos con información médica relevante.

## Características Clave
- 🖼️ Subida de imágenes dermatológicas con preprocesamiento
- 🧠 Análisis con modelo PyTorch de última generación
- 📊 Resultados detallados con visualización de áreas afectadas
- 📁 Historial de diagnósticos con seguimiento temporal
- 🔐 Autenticación JWT y gestión de perfiles
- 📱 Interfaz responsive optimizada para dispositivos móviles

## Tecnologías Implementadas

### Frontend
- **JavaScript Vanilla** (ES6+)
- **HTML5** (estructura semántica)
- **CSS3** con **Bootstrap 5** (diseño responsive)


### Backend
- **Python 3.10+**
- **FastAPI** (framework principal)
- **PostgreSQL** (base de datos relacional)
- **SQLAlchemy** (ORM)
- **Alembic** (gestión de migraciones)
- **JWT** (autenticación)
- **Uvicorn** (servidor ASGI)

### Modelo de Deep Learning
- **PyTorch 2.0+** (framework principal)
- **TorchVision** (modelos preentrenados)
- **OpenCV** (procesamiento de imágenes)
- **NumPy & Pandas** (manipulación de datos)
- **Scikit-learn** (métricas de evaluación)

### Infraestructura
- **Docker** (contenedorización)
- **Docker Compose** (orquestación)


## Estructura del Proyecto
medical_app/
├── backend/ # Servidor FastAPI
│ ├── alembic/ # Migraciones de base de datos
│ ├── app/ # Código principal
│ │ ├── api/ # Endpoints
│ │ ├── core/ # Configuración y seguridad
│ │ ├── db/ # Base de datos
│ │ ├── models/ # Modelos SQLAlchemy
│ │ ├── schemas/ # Pydantic schemas
│ │ └── services/ # Lógica de negocio
│ ├── tests/ # Pruebas unitarias
│ ├── Dockerfile
│ └── requirements.txt
├── frontend/ # Interfaz web
│ ├── assets/ # CSS, imágenes
│ ├── js/ # JavaScript
│ │ ├── auth.js # Autenticación
│ │ ├── diagnosis.js # Gestión de diagnósticos
│ │ └── utils.js # Utilidades
│ ├── index.html # Página principal
│ ├── dashboard.html # Panel de usuario
│ └── Dockerfile
├── model/ # Modelo PyTorch
│ ├── src/ # Código fuente
│ │ ├── inference.py # Predicción
│ │ ├── preprocessing.py # Procesamiento imágenes
│ │ └── train.py # Entrenamiento
│ ├── weights/ # Modelos entrenados
│ ├── Dockerfile
│ └── requirements.txt
├── docker-compose.yml # Configuración multi-servicio
└── nginx/ # Configuración proxy inverso
