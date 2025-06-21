# DermScan - Sistema de Diagnóstico Dermatológico Avanzado

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
