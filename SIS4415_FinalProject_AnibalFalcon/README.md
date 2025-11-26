# Smart Production Line Monitor - Final Project SIS4415

**Proyecto:** Opción A - Smart Production Line Monitor  
**Estudiante:** Anibal Simeon Falcon Castro  
**Curso:** SIS4415 - Informática en la Cuarta Revolución Industrial  
**Fecha:** 27 de Noviembre 2025

---

## Video Demostración

[Link al video en YouTube](TU_LINK_AQUI)

---

## Descripción del Proyecto

Sistema de monitoreo inteligente para líneas de producción que simula 3 máquinas industriales (MX-01, MX-02, MX-03) enviando datos en tiempo real sobre temperatura, vibración, producción y estado de fallas.

El sistema integra:
- Simulación IoT con Node-RED
- API REST con autenticación JWT
- API GraphQL con subscriptions en tiempo real
- Base de datos PostgreSQL
- Dashboard interactivo con controles y visualizaciones

---

## Tecnologías Utilizadas

### Backend
- **Python 3.13.7**
- **FastAPI 0.115.0** - Framework web asíncrono
- **SQLAlchemy 2.0.36** - ORM para base de datos
- **Strawberry GraphQL 0.243.0** - API GraphQL
- **Python-Jose** - Autenticación JWT
- **Passlib + Bcrypt** - Hash de contraseñas

### Base de Datos
- **PostgreSQL 16** (Docker)
- **psycopg 3.2.3** - Driver PostgreSQL

### Simulación y Visualización
- **Node-RED 4.1.1** - Simulador IoT y orquestador
- **Node-RED Dashboard 3.6.6** - Interfaz de usuario

### Infraestructura
- **Docker Compose** - Contenedorización de PostgreSQL
- **Uvicorn** - Servidor ASGI

---

## Estructura del Proyecto
```
SIS4415_FinalProject_AnibalFalcon/
├── api/                          # Backend FastAPI
│   ├── models/                   # Modelos SQLAlchemy
│   ├── schemas/                  # Schemas Pydantic
│   ├── routes/                   # Endpoints REST
│   ├── graphql/                  # Schema y resolvers GraphQL
│   ├── utils/                    # Utilidades (JWT, dependencies)
│   ├── config.py                 # Configuración
│   ├── database.py               # Conexión a BD
│   └── main.py                   # Aplicación principal
├── flows/                        # Flows de Node-RED
│   ├── smart_production_flow.json
│   └── complete_integrated_flow.json
├── screenshots/                  # Capturas de pantalla
├── Docker-4taRev/               # Configuración Docker
│   ├── docker-compose.yml
│   ├── .env
│   └── postgres/init.sql
├── venv/                        # Entorno virtual Python
├── .env                         # Variables de entorno
├── .gitignore
├── requirements.txt             # Dependencias Python
├── graphql_queries.md          # Queries de ejemplo
├── README.md                   # Este archivo
└── architecture.md             # Documentación de arquitectura
```

---

## Instalación y Configuración

### Prerrequisitos

- Python 3.9 o superior
- Node.js 14 o superior
- Docker y Docker Compose
- Git

### 1. Clonar el repositorio
```bash
git clone https://github.com/Falcon4s/Project_Smart-Production-Line-Monitor-.git
cd SIS4415_FinalProject_AnibalFalcon
```

### 2. Configurar Base de Datos (Docker)
```bash
cd Docker-4taRev
docker-compose up -d
cd ..
```

Verificar que PostgreSQL esté corriendo:
```bash
docker ps
```

### 3. Configurar Backend (FastAPI)

Crear entorno virtual:
```bash
python -m venv venv
```

Activar entorno virtual:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

Instalar dependencias:
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

El archivo `.env` ya está configurado con:
```env
DATABASE_URL=postgresql+psycopg://sis4415_user:production2025@localhost:5432/smart_production
SECRET_KEY=sis4415-smart-production-secret-key-change-in-production-2025
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Instalar Node-RED
```bash
npm install -g node-red
npm install -g node-red-dashboard
```

---

## Ejecución del Sistema

### Terminal 1: Iniciar FastAPI
```bash
cd SIS4415_FinalProject_AnibalFalcon
venv\Scripts\activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Iniciar Node-RED
```bash
node-red
```

Luego importar el flow:
1. Abrir http://localhost:1880
2. Menú > Import
3. Seleccionar `flows/complete_integrated_flow.json`
4. Deploy

---

## Acceso a las Interfaces

- **REST API (Swagger):** http://localhost:8000/docs
- **GraphQL Playground:** http://localhost:8000/graphql
- **Node-RED Editor:** http://localhost:1880
- **Dashboard de Producción:** http://localhost:1880/ui

---

## Credenciales de Prueba

### Usuario Default
- **Username:** `admin`
- **Password:** `admin123`

### Base de Datos
- **Host:** localhost
- **Port:** 5432
- **Database:** smart_production
- **User:** sis4415_user
- **Password:** production2025

---

## Uso del Sistema

### 1. Dashboard de Node-RED

Acceder a http://localhost:1880/ui

**Controles disponibles:**
- **Production Line:** Iniciar/detener simulación
- **Update Frequency:** Ajustar intervalo de envío (1-10 segundos)
- **Force Fault Mode:** Inyectar anomalías en los datos

**Visualizaciones:**
- Gauges de temperatura y vibración para cada máquina
- Gráfica de producción en tiempo real
- Estadísticas del sistema

### 2. API REST

Acceder a http://localhost:8000/docs

**Endpoints principales:**
- `GET /api/health` - Health check
- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/login` - Login (obtener JWT)
- `GET /api/machines` - Listar máquinas (requiere JWT)
- `GET /api/machines/status` - Estado actual (requiere JWT)
- `POST /api/machines/data` - Recibir datos de Node-RED

### 3. API GraphQL

Acceder a http://localhost:8000/graphql

Ver `graphql_queries.md` para queries de ejemplo.

**Queries principales:**
- `GetSystemOverview` - Vista completa del sistema
- `GetRecentMeasurements` - Historial de mediciones

**Subscriptions:**
- `LiveMachineData` - Datos en tiempo real (actualiza cada 2 seg)

---

## Flujo de Datos
```
Node-RED Simulator
       ↓
  (HTTP POST every 2s)
       ↓
REST API (/api/machines/data)
       ↓
PostgreSQL Database
       ↓
GraphQL API (queries/subscriptions)
       ↓
Dashboard / Clients
```

---

## Características Implementadas

- Simulación de 3 máquinas con datos realistas
- Inyección de anomalías para testing
- Autenticación JWT para endpoints protegidos
- API REST completa con documentación automática
- API GraphQL con queries y subscriptions
- Dashboard interactivo en tiempo real
- Base de datos relacional con PostgreSQL
- Sistema de alertas automático (triggers en BD)
- Vistas SQL para reportes
- Controles de frecuencia y estado

---

## Detener el Sistema

### Detener FastAPI
En la terminal de FastAPI: `Ctrl+C`

### Detener Node-RED
En la terminal de Node-RED: `Ctrl+C`

### Detener Docker
```bash
cd Docker-4taRev
docker-compose down
```

---

## Troubleshooting

### Error de conexión a base de datos
Verificar que Docker esté corriendo:
```bash
docker ps
```

### Error de módulos Python
Asegurarse de tener el entorno virtual activado:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Node-RED no muestra el dashboard
Verificar que node-red-dashboard esté instalado:
```bash
npm list -g node-red-dashboard
```

---

## Autor

**Anibal Simeon Falcon Castro**  
Universidad Anáhuac Mayab  
SIS4415 - Informática en la Cuarta Revolución Industrial  
Noviembre 2025