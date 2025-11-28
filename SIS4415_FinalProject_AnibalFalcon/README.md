# Smart Production Line Monitor - Final Project SIS4415

**Project:** Option A - Smart Production Line Monitor  
**Student:** Anibal Simeon Falcon Castro  
**Course:** SIS4415 - Information Technology in the Fourth Industrial Revolution  
**Date:** November 27, 2025

---

## Video Demonstration

**Link:** https://youtu.be/82AdWcQgD2c

---

## Project Description

An intelligent monitoring system for production lines that simulates 3 industrial machines (MX-01, MX-02, MX-03) sending real-time data about temperature, vibration, production, and fault status.

The system integrates:
- IoT simulation with Node-RED
- REST API with JWT authentication
- GraphQL API with real-time subscriptions
- PostgreSQL database with automatic triggers
- Interactive dashboard with controls and visualizations

---

## Technologies Used

### Backend
- **Python 3.13.7**
- **FastAPI 0.115.0** - Asynchronous web framework
- **SQLAlchemy 2.0.36** - Database ORM
- **Strawberry GraphQL 0.243.0** - GraphQL API
- **Python-Jose 3.3.0** - JWT authentication
- **Passlib + Bcrypt** - Password hashing

### Database
- **PostgreSQL 15** (Docker)
- **psycopg 3.2.3** - PostgreSQL driver

### Simulation and Visualization
- **Node.js 22.20.0**
- **Node-RED** - IoT simulator and orchestrator
- **Node-RED Dashboard** - User interface

### Infrastructure
- **Docker** - PostgreSQL containerization
- **Uvicorn 0.32.0** - ASGI server

---

## Project Structure
```
Final_Project/
├── Docker-4taRev/                   # Docker configuration
│   ├── docker-compose.yml
│   ├── .env
│   └── postgres/
│       └── init.sql                 # Database initialization script
│
└── SIS4415_FinalProject_AnibalFalcon/
    ├── api/                         # FastAPI backend
    │   ├── models/                  # SQLAlchemy models
    │   │   ├── __init__.py
    │   │   ├── user.py
    │   │   └── machine.py
    │   ├── schemas/                 # Pydantic schemas
    │   │   ├── __init__.py
    │   │   ├── user.py
    │   │   └── machine.py
    │   ├── routes/                  # REST endpoints
    │   │   ├── __init__.py
    │   │   ├── auth.py
    │   │   ├── machines.py
    │   │   └── alerts.py
    │   ├── graphql/                 # GraphQL schema and resolvers
    │   │   ├── __init__.py
    │   │   ├── schema.py
    │   │   ├── types.py
    │   │   └── resolvers.py
    │   ├── utils/                   # Utilities (JWT, dependencies)
    │   │   ├── __init__.py
    │   │   ├── security.py
    │   │   └── dependencies.py
    │   ├── config.py                # Configuration
    │   ├── database.py              # Database connection
    │   └── main.py                  # Main application
    ├── flows/                       # Node-RED flows
    │   └── complete_integrated_flow.json
    ├── screenshots/                 # System screenshots
    │   ├── 01_login_tab.png
    │   ├── 02_overview_tab.png
    │   ├── 03_live_metrics_tab.png
    │   ├── 04_alerts_tab.png
    │   ├── 05_reports_tab.png
    │   ├── 06_swagger_ui.png
    │   └── 07_graphql_playground.png
    ├── venv/                        # Python virtual environment
    ├── .env                         # Environment variables
    ├── .gitignore
    ├── requirements.txt             # Python dependencies
    ├── graphql_queries.md          # GraphQL query examples
    ├── architecture.md             # Architecture documentation
    └── README.md                   # This file
```

---

## Installation and Setup

### Prerequisites

- Python 3.13 or higher
- Node.js 22.20 or higher
- Docker and Docker Compose
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/Falcon4s/Project_Smart-Production-Line-Monitor-.git
cd Final_Project
```

### Step 2: Configure Database (Docker)
```bash
cd Docker-4taRev
docker-compose up -d
cd ..
```

Verify PostgreSQL is running:
```bash
docker ps
```

You should see a container named `postgres-sis4415` running.

### Step 3: Configure Backend (FastAPI)

Navigate to the project folder:
```bash
cd SIS4415_FinalProject_AnibalFalcon
```

Create virtual environment:
```bash
python -m venv venv
```

Activate virtual environment:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

Install dependencies:
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

The `.env` file is already configured with default values:
```env
DATABASE_URL=postgresql+psycopg://sis4415_user:production2025@localhost:5432/smart_production
SECRET_KEY=sis4415-smart-production-secret-key-change-in-production-2025
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Step 5: Install Node-RED
```bash
npm install -g node-red
```

Install dashboard nodes (in Node-RED user directory):
```bash
cd ~/.node-red
npm install node-red-dashboard
```

---

## Running the System

### Terminal 1: Start FastAPI
```bash
cd Final_Project/SIS4415_FinalProject_AnibalFalcon
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### Terminal 2: Start Node-RED
```bash
node-red
```

Expected output:
```
[info] Server now running at http://127.0.0.1:1880/
```

### Step 3: Import Node-RED Flow

1. Open http://localhost:1880 in your browser
2. Click menu (top right) > Import
3. Select file: `Final_Project/SIS4415_FinalProject_AnibalFalcon/flows/complete_integrated_flow.json`
4. Click Import
5. Click Deploy (red button, top right)

---

## Accessing the Interfaces

- **REST API (Swagger UI):** http://localhost:8000/docs
- **REST API (ReDoc):** http://localhost:8000/redoc
- **GraphQL Playground:** http://localhost:8000/graphql
- **Node-RED Editor:** http://localhost:1880
- **Production Dashboard:** http://localhost:1880/ui

---

## Default Credentials

### Dashboard User
- **Username:** `admin`
- **Password:** `admin123`

### Database Access
- **Host:** localhost
- **Port:** 5432
- **Database:** smart_production
- **User:** sis4415_user
- **Password:** production2025

---

## System Usage

### 1. Node-RED Dashboard

Access: http://localhost:1880/ui

**Tab 1: Login**
- Enter credentials to authenticate
- JWT token stored automatically

**Tab 2: Overview**
- System KPIs (throughput, faults, temperature)
- Machine status table with real-time updates

**Tab 3: Live Metrics**
- System controls (Start/Stop, Frequency, Fault Mode)
- Real-time gauges for all machines
- Production chart with live data

**Tab 4: Alerts**
- Active alerts table
- Clear all alerts button
- Auto-refresh every 10 seconds

**Tab 5: Reports**
- Time window selector (5, 15, 60 minutes)
- Generate statistics report
- Export data to CSV

**Available Controls:**
- **Production Line:** Start/stop simulation
- **Update Frequency:** Adjust send interval (1-10 seconds)
- **Force Fault Mode:** Inject anomalies in data

### 2. REST API

Access: http://localhost:8000/docs

**Authentication Endpoints:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (obtain JWT token)
- `GET /api/auth/me` - Get current user info (requires JWT)

**Machine Endpoints:**
- `POST /api/machines/data` - Receive telemetry from simulator (public)
- `GET /api/machines` - List all machines (requires JWT)
- `GET /api/machines/status` - Current status of all machines (requires JWT)
- `GET /api/machines/{machine_id}/measurements` - Measurement history (requires JWT)
- `GET /api/machines/stats` - Aggregated statistics (requires JWT)
- `GET /api/machines/export/csv` - Export measurements as CSV (requires JWT)

**Alert Endpoints:**
- `GET /api/alerts` - List alerts with filters (requires JWT)
- `PATCH /api/alerts/clear` - Clear all unresolved alerts (requires JWT)
- `PATCH /api/alerts/{alert_id}/resolve` - Resolve specific alert (requires JWT)

**Health Check:**
- `GET /api/health` - System health status (public)

### 3. GraphQL API

Access: http://localhost:8000/graphql

Refer to `graphql_queries.md` for example queries.

**Main Queries:**
- `machines` - Get all machines
- `measurements` - Get measurement history
- `machineStatus` - Get current machine status
- `allMachineStatuses` - Get all machine statuses

**Mutations:**
- `createMachine` - Register new machine
- `addMeasurement` - Add new measurement

**Subscriptions:**
- `machineUpdates` - Real-time machine updates (updates every 2 seconds)

---

## Data Flow
```
Node-RED Simulator
       |
       v (HTTP POST every 2 seconds)
       |
FastAPI REST API (/api/machines/data)
       |
       v (Insert + Trigger execution)
       |
PostgreSQL Database
       |
       v (Automatic alert generation via triggers)
       |
REST & GraphQL APIs
       |
       v (Query + Subscribe)
       |
Dashboard / Clients
```

---

## Implemented Features

**Backend:**
- JWT-based authentication with password hashing
- REST API with automatic OpenAPI documentation
- GraphQL API with queries, mutations, and subscriptions
- PostgreSQL database with automatic triggers for alerts
- SQL views for reporting
- CSV export functionality

**Frontend:**
- 5-tab interactive dashboard (Login, Overview, Live Metrics, Alerts, Reports)
- Real-time data visualization with charts and gauges
- System controls protected by authentication
- Alert management system

**Simulation:**
- 3 industrial machines (MX-01, MX-02, MX-03)
- Realistic data generation (temperature, vibration, production)
- Configurable update frequency (1-10 seconds)
- Fault injection mode for testing
- Automatic data transmission to backend

**Database:**
- Automatic alert generation via triggers
- Temperature threshold: > 90°C (critical)
- Vibration threshold: > 80 (high)
- Fault detection: immediate critical alert
- Time-series data storage with indexing

---

## Stopping the System

### Stop FastAPI
In the FastAPI terminal: `Ctrl+C`

### Stop Node-RED
In the Node-RED terminal: `Ctrl+C`

### Stop Docker
```bash
cd Final_Project/Docker-4taRev
docker-compose down
```

---

## Troubleshooting

### Database Connection Error
Verify Docker container is running:
```bash
docker ps
```

If not running, start it:
```bash
cd Final_Project/Docker-4taRev
docker-compose up -d
```

### Python Module Errors
Ensure virtual environment is activated:
```bash
cd Final_Project/SIS4415_FinalProject_AnibalFalcon
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Node-RED Dashboard Not Showing
Verify node-red-dashboard is installed:
```bash
cd ~/.node-red
npm list node-red-dashboard
```

If not installed:
```bash
npm install node-red-dashboard
```

### Port Already in Use
If port 8000 or 1880 is already in use, change the port:

**For FastAPI:**
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8001
```

**For Node-RED:**
Edit `~/.node-red/settings.js` and change `uiPort: 1880` to another port.

### Overview Tab Shows No Data
1. Verify you are logged in (check Login tab)
2. Verify simulator is running (Production Line toggle ON in Live Metrics)
3. Wait 5-10 seconds for data refresh
4. Check browser console (F12) for errors

---

## Additional Documentation

- **Architecture:** See `architecture.md` for complete system architecture documentation
- **GraphQL Queries:** See `graphql_queries.md` for query examples
- **Screenshots:** See `screenshots/` folder for system interface captures

---

## Author

**Anibal Simeon Falcon Castro**  
Universidad Anáhuac Mayab  
SIS4415 - Information Technology in the Fourth Industrial Revolution  
November 2025

---

## Acknowledgments

- Professor: Francisco Sosa Herrera
- Course: SIS4415 - Information Technology in the Fourth Industrial Revolution
- Institution: Universidad Anáhuac Mayab