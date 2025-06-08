# Servicio Académico

Este microservicio está diseñado para gestionar y procesar información académica de estudiantes, incluyendo calificaciones, asistencia, y métricas de rendimiento. El servicio proporciona una API robusta para la gestión de datos académicos y su integración con otros servicios del ecosistema.

## Características Principales

- Gestión completa de información académica:
  - Calificaciones y evaluaciones
  - Asistencia y participación
  - Historial académico
  - Métricas de rendimiento
- API RESTful con FastAPI
- Autenticación mediante tokens OAuth2
- Almacenamiento de datos en PostgreSQL
- Procesamiento asíncrono de datos
- Documentación automática de API con OpenAPI/Swagger

## Tecnologías Utilizadas

- **Backend Framework**: FastAPI 0.109.2
- **Base de Datos**: PostgreSQL
- **ORM**: SQLAlchemy 2.0.27
- **Procesamiento de Datos**: 
  - pandas 2.2.1
  - numpy 1.26.4
- **Autenticación**: python-jose[cryptography] 3.3.0
- **Variables de Entorno**: python-dotenv 1.0.1
- **Testing**: pytest 8.0.0

## Requisitos Previos

- Python 3.8 o superior
- PostgreSQL
- pip (gestor de paquetes de Python)

## Instalación Local

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd service-academic
```

2. Crear un entorno virtual e instalar dependencias:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configurar la base de datos:
```bash
# Crear la base de datos
psql -U postgres
CREATE DATABASE academic_service;
\q

# Ejecutar las migraciones
alembic upgrade head
```

4. Configurar variables de entorno:
   - Copiar el archivo `envs/.env.example` a `.env` en la raíz del proyecto
   - Completar las variables de entorno necesarias:
     - `PROJECT_NAME`: Nombre del proyecto (por defecto: "Academic Service")
     - `VERSION`: Versión del proyecto (por defecto: "1.0.0")
     - `DATABASE_URL`: URL de conexión a PostgreSQL
     - `API_AUTH_URL`: URL del servicio de autenticación

   Para producción, se puede usar el archivo `envs/.env.prod` como base.

5. Ejecutar el servidor de desarrollo:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 4002
```

El servidor estará disponible en `http://localhost:4002`

## Instalación con Docker

1. Construir la imagen:
```bash
docker build -t service-academic .
```

2. Ejecutar el contenedor:
```bash
docker run -d -p 4002:4002 --env-file envs/.env.prod --name service-academic service-academic
```

El servicio estará disponible en `http://localhost:4001`

## Uso de la API
Para ver todos los endpoints disponibles y su documentación detallada, visite la documentación interactiva de la API en:

http://localhost:4002/docs

Allí encontrará la lista completa de endpoints, sus parámetros, ejemplos de uso y respuestas.

La documentación completa de la API está disponible en `/docs` cuando el servidor está en ejecución.

## Estructura del Proyecto

```
service-academic/
├── app/
│   ├── controller/         # Controladores de la API
│   ├── core/              # Configuración central
│   ├── models/            # Modelos de base de datos
│   ├── schemas/           # Esquemas Pydantic
│   ├── services/          # Lógica de negocio
│   └── utils/             # Utilidades
├── migrations/            # Migraciones de Alembic
├── tests/                # Tests unitarios y de integración
├── main.py               # Punto de entrada de la aplicación
├── requirements.txt      # Dependencias del proyecto
└── .env                 # Variables de entorno
```

## Licencia

© 2025 Lucio Gabriel Abaca. Todos los derechos reservados. 