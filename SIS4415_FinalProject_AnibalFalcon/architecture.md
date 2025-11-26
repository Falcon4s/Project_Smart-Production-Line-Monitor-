# System Architecture Documentation
# Smart Production Line Monitor - SIS4415 Final Project

**Author:** Anibal Simeon Falcon Castro
**Course:** SIS4415 - Informática en la Cuarta Revolución Industrial
**Date:** November 2025
**Version:** 1.0.0

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Database Schema](#2-database-schema)
3. [REST API Endpoints](#3-rest-api-endpoints)
4. [GraphQL API Schema](#4-graphql-api-schema)
5. [End-to-End Data Flow](#5-end-to-end-data-flow)
6. [Security Architecture](#6-security-architecture)
7. [AWS Deployment Architecture](#7-aws-deployment-architecture)
8. [Cost Estimation](#8-cost-estimation)
9. [Scalability Strategy](#9-scalability-strategy)
10. [Monitoring and Observability](#10-monitoring-and-observability)

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────┐        ┌──────────────────────┐               │
│  │   Node-RED Dashboard │        │   External Clients   │               │
│  │   (localhost:1880/ui)│        │   (Mobile/Web Apps)  │               │
│  │                      │        │                      │               │
│  │  • Control Panel     │        │  • REST API Clients  │               │
│  │  • Live Monitoring   │        │  • GraphQL Clients   │               │
│  │  • Real-time Charts  │        │  • WebSocket Clients │               │
│  └──────────┬───────────┘        └──────────┬───────────┘               │
│             │                               │                           │
└─────────────┼───────────────────────────────┼───────────────────────────┘
              │                               │
              │      HTTP/WebSocket           │
              │                               │
┌─────────────┼───────────────────────────────┼───────────────────────────┐
│             │         APPLICATION LAYER     │                           │
├─────────────┼───────────────────────────────┼───────────────────────────┤
│             ▼                               ▼                           │
│  ┌─────────────────────────────────────────────────────────┐            │
│  │              FastAPI Server (Port 8000)                  │            │
│  │              Python 3.13 + Uvicorn ASGI                  │            │
│  ├──────────────────────────────────────────────────────────┤            │
│  │                                                           │            │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │            │
│  │  │   REST API   │  │  GraphQL API │  │   WebSocket   │  │            │
│  │  │   /api/v1    │  │   /graphql   │  │  Subscriptions│  │            │
│  │  │              │  │              │  │               │  │            │
│  │  │ • Health     │  │ • Queries    │  │ • Live Data   │  │            │
│  │  │ • Auth (JWT) │  │ • Mutations  │  │ • Real-time   │  │            │
│  │  │ • Machines   │  │ • Subscrip.  │  │   Updates     │  │            │
│  │  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘  │            │
│  │         │                 │                  │           │            │
│  │         └─────────────────┼──────────────────┘           │            │
│  │                           │                              │            │
│  │  ┌────────────────────────┴───────────────────────────┐  │            │
│  │  │         Business Logic Layer                       │  │            │
│  │  │  • SQLAlchemy ORM                                  │  │            │
│  │  │  • Pydantic Schemas                                │  │            │
│  │  │  • JWT Authentication                              │  │            │
│  │  │  • Password Hashing (bcrypt)                       │  │            │
│  │  └────────────────────────┬───────────────────────────┘  │            │
│  └──────────────────────────┼────────────────────────────────┘            │
│                             │                                             │
└─────────────────────────────┼─────────────────────────────────────────────┘
                              │ psycopg (PostgreSQL Driver)
                              │
┌─────────────────────────────┼─────────────────────────────────────────────┐
│                             │      DATA LAYER                             │
├─────────────────────────────┼─────────────────────────────────────────────┤
│                             ▼                                             │
│  ┌───────────────────────────────────────────────────────────┐            │
│  │        PostgreSQL 16 Database (Port 5432)                 │            │
│  ├───────────────────────────────────────────────────────────┤            │
│  │                                                            │            │
│  │  ┌──────────┐  ┌─────────────┐  ┌──────────────────┐     │            │
│  │  │  Tables  │  │   Indexes   │  │  Views & Funcs   │     │            │
│  │  │          │  │             │  │                  │     │            │
│  │  │ • users  │  │ • machine   │  │ • machine_stats  │     │            │
│  │  │ • mach's │  │   timestamp │  │   _24h           │     │            │
│  │  │ • measur │  │ • alerts    │  │ • active_alerts  │     │            │
│  │  │ • status │  │   unresolved│  │ • system_overview│     │            │
│  │  │ • alerts │  │             │  │ • auto_alerts    │     │            │
│  │  └──────────┘  └─────────────┘  └──────────────────┘     │            │
│  │                                                            │            │
│  └────────────────────────────────────────────────────────────┘            │
│                             ▲                                             │
└─────────────────────────────┼─────────────────────────────────────────────┘
                              │ HTTP POST (every 2 seconds)
                              │
┌─────────────────────────────┼─────────────────────────────────────────────┐
│                    IOT SIMULATION LAYER                                   │
├─────────────────────────────┼─────────────────────────────────────────────┤
│                             │                                             │
│  ┌──────────────────────────┴──────────────────────────────┐              │
│  │           Node-RED Flow Engine (Port 1880)              │              │
│  ├─────────────────────────────────────────────────────────┤              │
│  │                                                          │              │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │              │
│  │  │  Machine   │  │  Machine   │  │  Machine   │        │              │
│  │  │   MX-01    │  │   MX-02    │  │   MX-03    │        │              │
│  │  │            │  │            │  │            │        │              │
│  │  │ Assembly   │  │  Welding   │  │  Quality   │        │              │
│  │  │   Line     │  │  Station   │  │  Control   │        │              │
│  │  │   Alpha    │  │   Beta     │  │  Gamma     │        │              │
│  │  │            │  │            │  │            │        │              │
│  │  │ Temp: 60-90│  │ Temp: 65-95│  │ Temp: 55-85│        │              │
│  │  │ Vib: 10-40 │  │ Vib: 15-45 │  │ Vib: 10-35 │        │              │
│  │  │ Prod: 0-10 │  │ Prod: 0-8  │  │ Prod: 0-12 │        │              │
│  │  └────────────┘  └────────────┘  └────────────┘        │              │
│  │         │               │               │               │              │
│  │         └───────────────┴───────────────┘               │              │
│  │                         │                               │              │
│  │           ┌─────────────▼─────────────┐                 │              │
│  │           │  Data Aggregator Node     │                 │              │
│  │           │  • 2-second intervals     │                 │              │
│  │           │  • JSON formatting        │                 │              │
│  │           │  • Fault injection        │                 │              │
│  │           └─────────────┬─────────────┘                 │              │
│  │                         │                               │              │
│  │           ┌─────────────▼─────────────┐                 │              │
│  │           │  HTTP Request Node        │                 │              │
│  │           │  POST /api/v1/machines/   │                 │              │
│  │           │       data                │                 │              │
│  │           └───────────────────────────┘                 │              │
│  └──────────────────────────────────────────────────────────┘              │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Application** | FastAPI | 0.115.0 | Asynchronous web framework |
| | Uvicorn | 0.32.0 | ASGI server |
| | Python | 3.13.7 | Runtime environment |
| **API** | Strawberry GraphQL | 0.243.0 | GraphQL implementation |
| | Pydantic | 2.10.0 | Data validation |
| **Security** | Python-Jose | 3.3.0 | JWT token handling |
| | Passlib + Bcrypt | 1.7.4 | Password hashing |
| **Database** | PostgreSQL | 16 | Relational database |
| | SQLAlchemy | 2.0.36 | ORM |
| | psycopg | 3.2.3 | PostgreSQL driver |
| **IoT Simulation** | Node-RED | 4.1.1 | Flow orchestrator |
| | Node-RED Dashboard | 3.6.6 | UI components |
| **Infrastructure** | Docker Compose | - | Container orchestration |

### 1.3 System Components

#### Application Server (FastAPI)
- **Port:** 8000
- **Protocol:** HTTP/WebSocket
- **Concurrency Model:** Async/Await with Uvicorn ASGI
- **Features:**
  - Auto-generated OpenAPI documentation
  - CORS middleware for cross-origin requests
  - JWT-based authentication
  - WebSocket support for real-time subscriptions

#### Database (PostgreSQL)
- **Port:** 5432
- **Connection Pool:** SQLAlchemy engine with connection pooling
- **Features:**
  - ACID compliance
  - Triggers for automatic alert generation
  - Indexed queries for performance
  - Views for aggregated reporting

#### IoT Simulator (Node-RED)
- **Port:** 1880 (editor), 1880/ui (dashboard)
- **Simulation Rate:** 2 seconds per machine (configurable 1-10s)
- **Features:**
  - 3 independent machine simulators
  - Realistic sensor value generation
  - Fault injection capability
  - Interactive dashboard controls

---

## 2. Database Schema

### 2.1 Entity-Relationship Diagram

```
┌──────────────────────┐
│       users          │
├──────────────────────┤
│ PK id (SERIAL)       │
│ UK username (VARCHAR)│
│ UK email (VARCHAR)   │
│    password_hash     │
│    created_at        │
└──────────────────────┘

┌──────────────────────┐         1:N         ┌──────────────────────┐
│     machines         │◄────────────────────┤   measurements       │
├──────────────────────┤                     ├──────────────────────┤
│ PK id (SERIAL)       │                     │ PK id (SERIAL)       │
│ UK machine_id(VARCH) │                     │ FK machine_id(VARCH) │
│    name (VARCHAR)    │                     │    temperature(DEC)  │
│    location(VARCHAR) │                     │    vibration (INT)   │
│    status (VARCHAR)  │                     │    production_count  │
│    created_at(TIME)  │                     │    fault (BOOLEAN)   │
└──────────┬───────────┘                     │    timestamp (TIME)  │
           │                                 │    created_at (TIME) │
           │                                 └──────────────────────┘
           │                                 IDX: (machine_id, timestamp DESC)
           │
           │ 1:1
           ├────────────────────►┌──────────────────────┐
           │                     │   machine_status     │
           │                     ├──────────────────────┤
           │                     │ PK FK machine_id     │
           │                     │    temperature (DEC) │
           │                     │    vibration (INT)   │
           │                     │    production_count  │
           │                     │    fault (BOOLEAN)   │
           │                     │    last_updated(TIME)│
           │                     └──────────────────────┘
           │
           │ 1:N
           └────────────────────►┌──────────────────────┐
                                 │       alerts         │
                                 ├──────────────────────┤
                                 │ PK id (SERIAL)       │
                                 │ FK machine_id(VARCH) │
                                 │    alert_type(VARCH) │
                                 │    severity (VARCH)  │
                                 │    message (TEXT)    │
                                 │    resolved (BOOL)   │
                                 │    created_at (TIME) │
                                 │    resolved_at(TIME) │
                                 └──────────────────────┘
                                 IDX: (resolved, created_at DESC)
                                      WHERE resolved = FALSE
```

### 2.2 Complete SQL Schema

#### Core Tables

```sql
-- ============================================
-- TABLE: users
-- Purpose: JWT authentication and user management
-- ============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- ============================================
-- TABLE: machines
-- Purpose: Machine catalog and metadata
-- ============================================
CREATE TABLE machines (
    id SERIAL PRIMARY KEY,
    machine_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_machines_machine_id ON machines(machine_id);
CREATE INDEX idx_machines_status ON machines(status);

-- ============================================
-- TABLE: measurements
-- Purpose: Historical time-series data
-- Retention: 30 days (auto-cleanup via function)
-- ============================================
CREATE TABLE measurements (
    id SERIAL PRIMARY KEY,
    machine_id VARCHAR(20) REFERENCES machines(machine_id) ON DELETE CASCADE,
    temperature DECIMAL(5,2),
    vibration INTEGER,
    production_count INTEGER,
    fault BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- High-performance index for time-series queries
CREATE INDEX idx_measurements_machine_timestamp
ON measurements(machine_id, timestamp DESC);

-- ============================================
-- TABLE: machine_status
-- Purpose: Current state snapshot (optimized reads)
-- Pattern: Write-through cache
-- ============================================
CREATE TABLE machine_status (
    machine_id VARCHAR(20) PRIMARY KEY REFERENCES machines(machine_id) ON DELETE CASCADE,
    temperature DECIMAL(5,2),
    vibration INTEGER,
    production_count INTEGER,
    fault BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP NOT NULL
);

-- ============================================
-- TABLE: alerts
-- Purpose: System alerts and notifications
-- ============================================
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    machine_id VARCHAR(20) REFERENCES machines(machine_id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Partial index for fast unresolved alerts queries
CREATE INDEX idx_alerts_unresolved
ON alerts(resolved, created_at DESC)
WHERE resolved = FALSE;
```

#### Database Views

```sql
-- ============================================
-- VIEW: machine_stats_24h
-- Purpose: 24-hour rolling statistics per machine
-- Usage: Reporting and analytics dashboards
-- ============================================
CREATE VIEW machine_stats_24h AS
SELECT
    m.machine_id,
    m.name,
    m.location,
    COUNT(ms.id) as total_readings,
    ROUND(AVG(ms.temperature)::numeric, 2) as avg_temperature,
    ROUND(MAX(ms.temperature)::numeric, 2) as max_temperature,
    ROUND(MIN(ms.temperature)::numeric, 2) as min_temperature,
    ROUND(AVG(ms.vibration)::numeric, 2) as avg_vibration,
    MAX(ms.vibration) as max_vibration,
    MIN(ms.vibration) as min_vibration,
    SUM(ms.production_count) as total_production,
    COUNT(CASE WHEN ms.fault = TRUE THEN 1 END) as fault_count
FROM machines m
LEFT JOIN measurements ms ON m.machine_id = ms.machine_id
WHERE ms.timestamp > NOW() - INTERVAL '24 hours'
GROUP BY m.machine_id, m.name, m.location;

-- ============================================
-- VIEW: active_alerts
-- Purpose: Active alerts with priority sorting
-- ============================================
CREATE VIEW active_alerts AS
SELECT
    a.id,
    a.machine_id,
    m.name as machine_name,
    m.location,
    a.alert_type,
    a.severity,
    a.message,
    a.created_at,
    ROUND(EXTRACT(EPOCH FROM (NOW() - a.created_at))/60) as minutes_open
FROM alerts a
JOIN machines m ON a.machine_id = m.machine_id
WHERE a.resolved = FALSE
ORDER BY
    CASE a.severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    a.created_at DESC;

-- ============================================
-- VIEW: system_overview
-- Purpose: High-level system metrics
-- ============================================
CREATE VIEW system_overview AS
SELECT
    (SELECT COUNT(*) FROM machines WHERE status = 'active') as active_machines,
    (SELECT COUNT(*) FROM machines) as total_machines,
    (SELECT COUNT(*) FROM alerts WHERE resolved = FALSE) as active_alerts,
    (SELECT SUM(production_count) FROM machine_status) as current_total_production,
    (SELECT AVG(temperature) FROM machine_status) as avg_system_temperature,
    (SELECT MAX(vibration) FROM machine_status) as max_system_vibration;
```

#### Database Functions and Triggers

```sql
-- ============================================
-- FUNCTION: cleanup_old_measurements
-- Purpose: Data retention management (30 days)
-- Schedule: Run daily via cron or pg_cron
-- ============================================
CREATE OR REPLACE FUNCTION cleanup_old_measurements()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM measurements
    WHERE timestamp < NOW() - INTERVAL '30 days';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: check_and_create_alert
-- Purpose: Automatic alert generation based on thresholds
-- Trigger: ON INSERT to measurements table
-- ============================================
CREATE OR REPLACE FUNCTION check_and_create_alert()
RETURNS TRIGGER AS $$
BEGIN
    -- Critical: Temperature > 90°C
    IF NEW.temperature > 90 THEN
        INSERT INTO alerts (machine_id, alert_type, severity, message)
        VALUES (NEW.machine_id, 'high_temperature', 'critical',
                'Temperature exceeded 90°C: ' || NEW.temperature || '°C');
    END IF;

    -- High: Vibration > 80
    IF NEW.vibration > 80 THEN
        INSERT INTO alerts (machine_id, alert_type, severity, message)
        VALUES (NEW.machine_id, 'high_vibration', 'high',
                'Vibration exceeded safe threshold: ' || NEW.vibration);
    END IF;

    -- Critical: Fault condition
    IF NEW.fault = TRUE THEN
        INSERT INTO alerts (machine_id, alert_type, severity, message)
        VALUES (NEW.machine_id, 'machine_fault', 'critical',
                'Machine reported a fault condition');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger definition
CREATE TRIGGER trigger_alert_on_measurement
AFTER INSERT ON measurements
FOR EACH ROW
EXECUTE FUNCTION check_and_create_alert();
```

### 2.3 Data Dictionary

| Table | Column | Type | Constraints | Description |
|-------|--------|------|-------------|-------------|
| **users** | id | SERIAL | PK | Auto-incrementing user ID |
| | username | VARCHAR(50) | UNIQUE, NOT NULL | Unique username for login |
| | email | VARCHAR(100) | UNIQUE, NOT NULL | User email address |
| | password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| | created_at | TIMESTAMP | DEFAULT NOW() | Account creation timestamp |
| **machines** | id | SERIAL | PK | Auto-incrementing machine ID |
| | machine_id | VARCHAR(20) | UNIQUE, NOT NULL | Business key (e.g., MX-01) |
| | name | VARCHAR(100) | NOT NULL | Human-readable machine name |
| | location | VARCHAR(100) | | Physical location |
| | status | VARCHAR(20) | DEFAULT 'active' | Operational status |
| | created_at | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |
| **measurements** | id | SERIAL | PK | Auto-incrementing measurement ID |
| | machine_id | VARCHAR(20) | FK → machines | Reference to machine |
| | temperature | DECIMAL(5,2) | | Temperature in Celsius |
| | vibration | INTEGER | | Vibration intensity (0-100) |
| | production_count | INTEGER | | Production increment |
| | fault | BOOLEAN | DEFAULT FALSE | Fault indicator |
| | timestamp | TIMESTAMP | NOT NULL | Measurement timestamp |
| | created_at | TIMESTAMP | DEFAULT NOW() | Database insert timestamp |
| **machine_status** | machine_id | VARCHAR(20) | PK, FK → machines | Machine reference |
| | temperature | DECIMAL(5,2) | | Current temperature |
| | vibration | INTEGER | | Current vibration |
| | production_count | INTEGER | | Cumulative production |
| | fault | BOOLEAN | DEFAULT FALSE | Current fault state |
| | last_updated | TIMESTAMP | NOT NULL | Last update timestamp |
| **alerts** | id | SERIAL | PK | Auto-incrementing alert ID |
| | machine_id | VARCHAR(20) | FK → machines | Machine reference |
| | alert_type | VARCHAR(50) | NOT NULL | Alert category |
| | severity | VARCHAR(20) | NOT NULL | critical/high/medium/low |
| | message | TEXT | | Alert description |
| | resolved | BOOLEAN | DEFAULT FALSE | Resolution status |
| | created_at | TIMESTAMP | DEFAULT NOW() | Alert creation time |
| | resolved_at | TIMESTAMP | | Resolution timestamp |

---

## 3. REST API Endpoints

### 3.1 API Structure

**Base URL:** `http://localhost:8000`
**API Prefix:** `/api/v1`
**Documentation:** `/docs` (Swagger UI), `/redoc` (ReDoc)

### 3.2 Endpoint Catalog

#### Health Check

```http
GET /api/v1/health
```

**Description:** System health check endpoint
**Authentication:** None
**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-26T10:30:00Z"
}
```

---

#### Authentication Endpoints

##### Register New User

```http
POST /api/v1/auth/register
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2025-11-26T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Username or email already exists
- `422 Unprocessable Entity` - Invalid request body

---

##### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
```

**Request Body:**
```
username=admin&password=admin123
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials

---

##### Get Current User

```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@smartproduction.com",
  "created_at": "2025-11-26T10:30:00Z"
}
```

---

#### Machine Endpoints

##### Receive Machine Data (Node-RED)

```http
POST /api/v1/machines/data
Content-Type: application/json
```

**Description:** Endpoint for Node-RED to send sensor data
**Authentication:** None (public endpoint for IoT integration)
**Request Body:**
```json
{
  "machine_id": "MX-01",
  "temperature": 72.5,
  "vibration": 25,
  "production_count": 5,
  "fault": false,
  "timestamp": "2025-11-26T10:30:00Z"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Data received"
}
```

**Error Responses:**
- `404 Not Found` - Machine ID not found
- `422 Unprocessable Entity` - Invalid data format

---

##### List All Machines

```http
GET /api/v1/machines
Authorization: Bearer <token>
```

**Description:** Get catalog of all machines
**Authentication:** Required (JWT)
**Response (200 OK):**
```json
[
  {
    "id": 1,
    "machine_id": "MX-01",
    "name": "Assembly Line Alpha",
    "location": "Building A - Floor 1",
    "status": "active",
    "created_at": "2025-11-26T08:00:00Z"
  },
  {
    "id": 2,
    "machine_id": "MX-02",
    "name": "Welding Station Beta",
    "location": "Building A - Floor 2",
    "status": "active",
    "created_at": "2025-11-26T08:00:00Z"
  },
  {
    "id": 3,
    "machine_id": "MX-03",
    "name": "Quality Control Gamma",
    "location": "Building B - Floor 1",
    "status": "active",
    "created_at": "2025-11-26T08:00:00Z"
  }
]
```

---

##### Get Machines Status

```http
GET /api/v1/machines/status
Authorization: Bearer <token>
```

**Description:** Get current status of all machines
**Authentication:** Required (JWT)
**Response (200 OK):**
```json
[
  {
    "machine_id": "MX-01",
    "temperature": 72.5,
    "vibration": 25,
    "production_count": 1250,
    "fault": false,
    "last_updated": "2025-11-26T10:30:00Z"
  },
  {
    "machine_id": "MX-02",
    "temperature": 85.3,
    "vibration": 35,
    "production_count": 980,
    "fault": false,
    "last_updated": "2025-11-26T10:30:00Z"
  },
  {
    "machine_id": "MX-03",
    "temperature": 68.1,
    "vibration": 18,
    "production_count": 1450,
    "fault": false,
    "last_updated": "2025-11-26T10:30:00Z"
  }
]
```

---

##### Get Machine Measurements

```http
GET /api/v1/machines/{machine_id}/measurements?limit=100
Authorization: Bearer <token>
```

**Description:** Get historical measurements for a specific machine
**Authentication:** Required (JWT)
**Parameters:**
- `machine_id` (path) - Machine identifier (e.g., MX-01)
- `limit` (query) - Number of records (default: 100)

**Response (200 OK):**
```json
[
  {
    "id": 5432,
    "machine_id": "MX-01",
    "temperature": 72.5,
    "vibration": 25,
    "production_count": 5,
    "fault": false,
    "timestamp": "2025-11-26T10:30:00Z",
    "created_at": "2025-11-26T10:30:01Z"
  },
  {
    "id": 5431,
    "machine_id": "MX-01",
    "temperature": 71.8,
    "vibration": 24,
    "production_count": 4,
    "fault": false,
    "timestamp": "2025-11-26T10:29:58Z",
    "created_at": "2025-11-26T10:29:59Z"
  }
]
```

**Error Responses:**
- `404 Not Found` - No measurements found for machine

---

### 3.3 Authentication Flow

```
Client                          API Server                     Database
  │                                 │                              │
  │ 1. POST /auth/register         │                              │
  ├────────────────────────────────►│                              │
  │    {username, email, password}  │                              │
  │                                 │ 2. Hash password (bcrypt)    │
  │                                 │ 3. INSERT INTO users         │
  │                                 ├─────────────────────────────►│
  │                                 │ 4. User created              │
  │                                 │◄─────────────────────────────┤
  │ 5. {id, username, email}       │                              │
  │◄────────────────────────────────┤                              │
  │                                 │                              │
  │ 6. POST /auth/login            │                              │
  ├────────────────────────────────►│                              │
  │    {username, password}         │                              │
  │                                 │ 7. SELECT user by username   │
  │                                 ├─────────────────────────────►│
  │                                 │ 8. User record               │
  │                                 │◄─────────────────────────────┤
  │                                 │ 9. Verify password (bcrypt)  │
  │                                 │ 10. Generate JWT token       │
  │ 11. {access_token, token_type} │                              │
  │◄────────────────────────────────┤                              │
  │                                 │                              │
  │ 12. GET /machines              │                              │
  │     Authorization: Bearer <JWT> │                              │
  ├────────────────────────────────►│                              │
  │                                 │ 13. Validate JWT signature   │
  │                                 │ 14. Extract username         │
  │                                 │ 15. SELECT machines          │
  │                                 ├─────────────────────────────►│
  │                                 │ 16. Machine list             │
  │                                 │◄─────────────────────────────┤
  │ 17. [machine objects]          │                              │
  │◄────────────────────────────────┤                              │
```

---

## 4. GraphQL API Schema

### 4.1 GraphQL Endpoint

**URL:** `http://localhost:8000/graphql`
**Protocol:** HTTP POST (queries/mutations), WebSocket (subscriptions)
**Playground:** Interactive GraphQL IDE available at endpoint

### 4.2 Schema Definition

```graphql
# ============================================
# TYPES
# ============================================

type Machine {
  machineId: String!
  name: String!
  location: String
  status: String!
  createdAt: DateTime!
}

type MachineStatus {
  machineId: String!
  temperature: Float
  vibration: Int
  productionCount: Int
  fault: Boolean!
  lastUpdated: DateTime!
}

type Measurement {
  id: Int!
  machineId: String!
  temperature: Float
  vibration: Int
  productionCount: Int
  fault: Boolean!
  timestamp: DateTime!
  createdAt: DateTime!
}

type Alert {
  id: Int!
  machineId: String!
  alertType: String!
  severity: String!
  message: String
  resolved: Boolean!
  createdAt: DateTime!
  resolvedAt: DateTime
}

type SystemStats {
  totalMachines: Int!
  activeMachines: Int!
  totalMeasurements: Int!
  activeAlerts: Int!
  avgSystemTemperature: Float
  maxSystemVibration: Int
}

# ============================================
# QUERIES
# ============================================

type Query {
  # Machine queries
  machines: [Machine!]!
  machine(machineId: String!): Machine

  # Status queries
  machinesStatus: [MachineStatus!]!
  machineStatus(machineId: String!): MachineStatus

  # Measurement queries
  measurements(
    machineId: String
    limit: Int = 100
    startTime: DateTime
    endTime: DateTime
  ): [Measurement!]!

  # Alert queries
  alerts(
    machineId: String
    resolved: Boolean
    severity: String
    limit: Int = 50
  ): [Alert!]!

  # System statistics
  systemStats: SystemStats!
}

# ============================================
# MUTATIONS
# ============================================

type Mutation {
  # Alert management
  resolveAlert(alertId: Int!): Alert!

  # Machine management
  updateMachineStatus(
    machineId: String!
    status: String!
  ): Machine!
}

# ============================================
# SUBSCRIPTIONS (WebSocket)
# ============================================

type Subscription {
  # Real-time machine data (updates every 2 seconds)
  liveMachineData: [MachineStatus!]!

  # Real-time alerts
  newAlert: Alert!
}

# ============================================
# SCALARS
# ============================================

scalar DateTime
```

### 4.3 Query Examples

#### Get System Overview

```graphql
query GetSystemOverview {
  machines {
    machineId
    name
    location
    status
  }
  machinesStatus {
    machineId
    temperature
    vibration
    productionCount
    fault
    lastUpdated
  }
  systemStats {
    totalMachines
    activeMachines
    totalMeasurements
    activeAlerts
    avgSystemTemperature
    maxSystemVibration
  }
}
```

**Response:**
```json
{
  "data": {
    "machines": [
      {
        "machineId": "MX-01",
        "name": "Assembly Line Alpha",
        "location": "Building A - Floor 1",
        "status": "active"
      },
      {
        "machineId": "MX-02",
        "name": "Welding Station Beta",
        "location": "Building A - Floor 2",
        "status": "active"
      },
      {
        "machineId": "MX-03",
        "name": "Quality Control Gamma",
        "location": "Building B - Floor 1",
        "status": "active"
      }
    ],
    "machinesStatus": [
      {
        "machineId": "MX-01",
        "temperature": 72.5,
        "vibration": 25,
        "productionCount": 1250,
        "fault": false,
        "lastUpdated": "2025-11-26T10:30:00Z"
      }
    ],
    "systemStats": {
      "totalMachines": 3,
      "activeMachines": 3,
      "totalMeasurements": 54320,
      "activeAlerts": 0,
      "avgSystemTemperature": 71.5,
      "maxSystemVibration": 35
    }
  }
}
```

---

#### Get Recent Measurements

```graphql
query GetRecentMeasurements {
  measurements(limit: 10) {
    machineId
    temperature
    vibration
    productionCount
    timestamp
  }
}
```

---

#### Get Active Alerts

```graphql
query GetActiveAlerts {
  alerts(resolved: false) {
    id
    machineId
    alertType
    severity
    message
    createdAt
  }
}
```

---

#### Resolve Alert (Mutation)

```graphql
mutation ResolveAlert {
  resolveAlert(alertId: 123) {
    id
    resolved
    resolvedAt
  }
}
```

---

### 4.4 Subscription Example

#### Live Machine Data Stream

```graphql
subscription LiveMachineData {
  liveMachineData {
    machineId
    temperature
    vibration
    productionCount
    fault
    lastUpdated
  }
}
```

**WebSocket Connection:**
```javascript
// Client-side JavaScript example
const ws = new WebSocket('ws://localhost:8000/graphql');

ws.send(JSON.stringify({
  type: 'connection_init'
}));

ws.send(JSON.stringify({
  id: '1',
  type: 'start',
  payload: {
    query: `
      subscription {
        liveMachineData {
          machineId
          temperature
          vibration
          productionCount
          fault
          lastUpdated
        }
      }
    `
  }
}));

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

**Stream Response (every 2 seconds):**
```json
{
  "type": "data",
  "id": "1",
  "payload": {
    "data": {
      "liveMachineData": [
        {
          "machineId": "MX-01",
          "temperature": 72.5,
          "vibration": 25,
          "productionCount": 1250,
          "fault": false,
          "lastUpdated": "2025-11-26T10:30:00Z"
        },
        {
          "machineId": "MX-02",
          "temperature": 85.3,
          "vibration": 35,
          "productionCount": 980,
          "fault": false,
          "lastUpdated": "2025-11-26T10:30:00Z"
        },
        {
          "machineId": "MX-03",
          "temperature": 68.1,
          "vibration": 18,
          "productionCount": 1450,
          "fault": false,
          "lastUpdated": "2025-11-26T10:30:00Z"
        }
      ]
    }
  }
}
```

---

## 5. End-to-End Data Flow

### 5.1 Complete Data Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 1: IoT Simulation (Node-RED)                                      │
│ Interval: 2 seconds (configurable 1-10s)                               │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │ Generate sensor data:
                               │ • Temperature: Random in range
                               │ • Vibration: Random in range
                               │ • Production: Random increment
                               │ • Fault: Randomly injected
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Machine Simulators (Function Nodes)                                    │
│                                                                         │
│ MX-01: temp=60-90°C, vib=10-40, prod=0-10                             │
│ MX-02: temp=65-95°C, vib=15-45, prod=0-8                              │
│ MX-03: temp=55-85°C, vib=10-35, prod=0-12                             │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │ JSON payload:
                               │ {
                               │   "machine_id": "MX-01",
                               │   "temperature": 72.5,
                               │   "vibration": 25,
                               │   "production_count": 5,
                               │   "fault": false,
                               │   "timestamp": "2025-11-26T10:30:00Z"
                               │ }
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 2: HTTP Request (Node-RED)                                        │
│ POST http://localhost:8000/api/v1/machines/data                        │
│ Content-Type: application/json                                         │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │ Network: HTTP/1.1
                               │ Latency: ~10-50ms (localhost)
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 3: FastAPI Server (Uvicorn ASGI)                                  │
│ Endpoint: /api/v1/machines/data                                        │
│ Handler: receive_machine_data()                                        │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │ 3.1: Validate request (Pydantic)
                               │ 3.2: Check machine exists
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Database Operations (SQLAlchemy ORM)                           │
│                                                                         │
│ Transaction Start                                                       │
│ ├─► INSERT INTO measurements (...) VALUES (...)                        │
│ │                                                                       │
│ ├─► TRIGGER: trigger_alert_on_measurement                              │
│ │   └─► IF temperature > 90 THEN INSERT INTO alerts (...)             │
│ │   └─► IF vibration > 80 THEN INSERT INTO alerts (...)               │
│ │   └─► IF fault = TRUE THEN INSERT INTO alerts (...)                 │
│ │                                                                       │
│ ├─► UPDATE machine_status SET                                          │
│ │       temperature = 72.5,                                            │
│ │       vibration = 25,                                                │
│ │       production_count = production_count + 5,                       │
│ │       fault = false,                                                 │
│ │       last_updated = '2025-11-26T10:30:00Z'                          │
│ │   WHERE machine_id = 'MX-01'                                         │
│ │                                                                       │
│ └─► COMMIT                                                             │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │ Success: 201 Created
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Response to Node-RED                                           │
│ {"status": "success", "message": "Data received"}                      │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               │ Data now available via:
                               │ • REST API (GET endpoints)
                               │ • GraphQL (queries)
                               │ • WebSocket (subscriptions)
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 6: Data Consumption                                               │
│                                                                         │
│ ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│ │ Node-RED Dashbd  │  │ GraphQL Clients  │  │ External Apps    │      │
│ │ GET /machines/   │  │ subscription {   │  │ REST API calls   │      │
│ │     status       │  │   liveMachineData│  │ with JWT         │      │
│ └──────────────────┘  └──────────────────┘  └──────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow Timing Diagram

```
Time   Node-RED          FastAPI             PostgreSQL         GraphQL WS
(ms)                                                            Clients
─────────────────────────────────────────────────────────────────────────
  0    Generate data
       MX-01, MX-02,
       MX-03

 10    POST /data ────►
       (3 requests)

 20                     Validate ───────► BEGIN TX
                        requests

 30                                       INSERT measurements
                                         (3 rows)

 40                                       TRIGGER checks
                                         (alert thresholds)

 50                                       UPDATE machine_status
                                         (3 rows)

 60                                       COMMIT TX

 70                     ◄────────────── Success

 80    ◄──────────── 201 Created
       (3 responses)

 90                     Broadcast ───────────────────────────► WS Push
                        via WS                                  (new data)
                        subscription

2000   [Repeat cycle every 2 seconds]
```

### 5.3 Data Persistence Strategy

#### Write Path (Node-RED → Database)
1. **Dual-write pattern:**
   - Insert to `measurements` table (historical record)
   - Upsert to `machine_status` table (current snapshot)

2. **Consistency guarantee:**
   - Both writes in same database transaction
   - ACID properties ensure atomicity

3. **Trigger execution:**
   - Automatic alert generation on threshold violations
   - Executes within same transaction

#### Read Path (Clients → Database)
1. **Current status queries:**
   - Read from `machine_status` table (O(1) lookup)
   - Optimized for low latency

2. **Historical queries:**
   - Read from `measurements` table with time-range filter
   - Index on `(machine_id, timestamp DESC)` for fast scans

3. **Aggregated reports:**
   - Use materialized views (`machine_stats_24h`)
   - Pre-computed statistics

---

## 6. Security Architecture

### 6.1 Authentication Mechanism

#### JWT (JSON Web Token) Implementation

```
┌─────────────────────────────────────────────────────────────────────────┐
│ JWT Token Structure                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ HEADER                                                                  │
│ {                                                                       │
│   "alg": "HS256",    ← HMAC-SHA256 algorithm                          │
│   "typ": "JWT"                                                          │
│ }                                                                       │
│                                                                         │
│ PAYLOAD                                                                 │
│ {                                                                       │
│   "sub": "admin",           ← Subject (username)                       │
│   "exp": 1732621800,        ← Expiration (Unix timestamp)              │
│   "iat": 1732620000         ← Issued at                                │
│ }                                                                       │
│                                                                         │
│ SIGNATURE                                                               │
│ HMACSHA256(                                                             │
│   base64UrlEncode(header) + "." +                                       │
│   base64UrlEncode(payload),                                             │
│   SECRET_KEY                ← Stored in environment variable           │
│ )                                                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

Final Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTczMjYyMTgwMCwiaWF0IjoxNzMyNjIwMDAwfQ.SIGNATURE_HASH
```

#### Password Security

```python
# Hashing Algorithm: bcrypt with salt rounds
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password storage flow:
plaintext_password = "admin123"
                ↓
hashed_password = pwd_context.hash(plaintext_password)
# Result: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeWgdx5SbHa0X0YRi
                ↓
Store in database (users.password_hash)

# Password verification flow:
provided_password = "admin123"
stored_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeWgdx5SbHa0X0YRi"
                ↓
is_valid = pwd_context.verify(provided_password, stored_hash)
# Result: True
```

### 6.2 Authorization Flow

```
┌─────────────┐                  ┌─────────────┐                  ┌──────────┐
│   Client    │                  │  API Server │                  │ Database │
└──────┬──────┘                  └──────┬──────┘                  └────┬─────┘
       │                                │                              │
       │ 1. POST /auth/login           │                              │
       │    {username, password}        │                              │
       ├───────────────────────────────►│                              │
       │                                │ 2. Verify credentials         │
       │                                ├─────────────────────────────►│
       │                                │◄─────────────────────────────┤
       │                                │ 3. Generate JWT (30 min TTL) │
       │ 4. {access_token}             │                              │
       │◄───────────────────────────────┤                              │
       │                                │                              │
       │ [Client stores token]          │                              │
       │                                │                              │
       │ 5. GET /machines               │                              │
       │    Authorization: Bearer <JWT> │                              │
       ├───────────────────────────────►│                              │
       │                                │ 6. Validate JWT:             │
       │                                │    ✓ Signature valid?        │
       │                                │    ✓ Not expired?            │
       │                                │    ✓ Subject exists?         │
       │                                │                              │
       │                                │ 7. Extract username from JWT │
       │                                │ 8. Query machines            │
       │                                ├─────────────────────────────►│
       │                                │◄─────────────────────────────┤
       │ 9. [machine list]             │                              │
       │◄───────────────────────────────┤                              │
       │                                │                              │
       │                                │                              │
       │ After 30 minutes:              │                              │
       │                                │                              │
       │ 10. GET /machines              │                              │
       │     Authorization: Bearer <JWT>│                              │
       ├───────────────────────────────►│                              │
       │                                │ 11. Validate JWT:            │
       │                                │     ✗ Token expired          │
       │ 12. 401 Unauthorized           │                              │
       │◄───────────────────────────────┤                              │
       │                                │                              │
       │ 13. Re-login required          │                              │
```

### 6.3 Endpoint Security Matrix

| Endpoint | Authentication | Authorization | Public Access |
|----------|---------------|---------------|---------------|
| `GET /` | ❌ None | ❌ None | ✅ Yes |
| `GET /api/v1/health` | ❌ None | ❌ None | ✅ Yes |
| `POST /api/v1/auth/register` | ❌ None | ❌ None | ✅ Yes |
| `POST /api/v1/auth/login` | ❌ None | ❌ None | ✅ Yes |
| `POST /api/v1/machines/data` | ❌ None | ❌ None | ✅ Yes (IoT) |
| `GET /api/v1/auth/me` | ✅ JWT | ✅ Self | ❌ No |
| `GET /api/v1/machines` | ✅ JWT | ✅ Authenticated | ❌ No |
| `GET /api/v1/machines/status` | ✅ JWT | ✅ Authenticated | ❌ No |
| `GET /api/v1/machines/{id}/measurements` | ✅ JWT | ✅ Authenticated | ❌ No |
| `GraphQL queries` | ⚠️ Optional | ⚠️ Optional | ⚠️ Mixed |
| `GraphQL subscriptions` | ⚠️ Optional | ⚠️ Optional | ⚠️ Mixed |

**Note:** `/machines/data` is intentionally public to allow Node-RED integration without token management complexity. In production, this should be secured with API keys or IP whitelisting.

### 6.4 Security Best Practices Implemented

#### ✅ Implemented
- **Password Hashing:** bcrypt with automatic salt generation
- **JWT Signing:** HMAC-SHA256 with secret key
- **Token Expiration:** 30-minute TTL (configurable)
- **CORS Middleware:** Cross-origin request handling
- **SQL Injection Protection:** SQLAlchemy parameterized queries
- **Input Validation:** Pydantic schemas for all request bodies
- **HTTPS Ready:** Production deployment with TLS/SSL

#### ⚠️ Production Recommendations
- **Rate Limiting:** Implement request throttling (e.g., 100 req/min per IP)
- **API Key for IoT:** Replace public `/machines/data` with API key auth
- **Refresh Tokens:** Implement refresh token rotation
- **Role-Based Access Control (RBAC):** Add user roles (admin, operator, viewer)
- **Audit Logging:** Log all authentication attempts and data modifications
- **Input Sanitization:** Additional validation for XSS prevention
- **Database Encryption:** Enable PostgreSQL TDE (Transparent Data Encryption)
- **Secrets Management:** Use AWS Secrets Manager or HashiCorp Vault

---

## 7. AWS Deployment Architecture

### 7.1 Production Infrastructure Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              AWS Cloud                                  │
│                         Region: us-east-1                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │
┌───────────────────────────────────┼─────────────────────────────────────┐
│                       Route 53 DNS Service                              │
│                                   │                                     │
│  smartproduction.example.com ────►│                                     │
│  api.smartproduction.example.com  │                                     │
└───────────────────────────────────┼─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 CloudFront CDN (Optional)                               │
│  • TLS/SSL termination                                                  │
│  • DDoS protection (AWS Shield)                                         │
│  • Geographic distribution                                              │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              Application Load Balancer (ALB)                            │
│  • Health checks: /api/v1/health                                        │
│  • SSL/TLS certificate (ACM)                                            │
│  • Target groups: ECS tasks                                             │
│  • Availability Zones: us-east-1a, us-east-1b                          │
└─────────────────────────────────────────────────────────────────────────┘
                    │                              │
                    │                              │
    ┌───────────────┴────────────┐    ┌───────────┴────────────┐
    │  Availability Zone 1a      │    │  Availability Zone 1b  │
    │  (Primary)                 │    │  (Failover)            │
    └────────────────────────────┘    └────────────────────────┘
                    │                              │
    ┌───────────────▼────────────┐    ┌───────────▼────────────┐
    │  Public Subnet             │    │  Public Subnet         │
    │  10.0.1.0/24               │    │  10.0.2.0/24           │
    └────────────────────────────┘    └────────────────────────┘
                    │                              │
    ┌───────────────▼────────────┐    ┌───────────▼────────────┐
    │  ECS Fargate Tasks         │    │  ECS Fargate Tasks     │
    │                            │    │                        │
    │  ┌──────────────────────┐  │    │  ┌──────────────────┐  │
    │  │ FastAPI Container    │  │    │  │ FastAPI Container│  │
    │  │ • 2 vCPU             │  │    │  │ • 2 vCPU         │  │
    │  │ • 4 GB RAM           │  │    │  │ • 4 GB RAM       │  │
    │  │ • Port 8000          │  │    │  │ • Port 8000      │  │
    │  └──────────────────────┘  │    │  └──────────────────┘  │
    │                            │    │                        │
    │  ┌──────────────────────┐  │    │  ┌──────────────────┐  │
    │  │ Node-RED Container   │  │    │  │ Node-RED Contain │  │
    │  │ • 1 vCPU             │  │    │  │ • 1 vCPU         │  │
    │  │ • 2 GB RAM           │  │    │  │ • 2 GB RAM       │  │
    │  │ • Port 1880          │  │    │  │ • Port 1880      │  │
    │  └──────────────────────┘  │    │  └──────────────────┘  │
    └────────────────────────────┘    └────────────────────────┘
                    │                              │
                    └──────────────┬───────────────┘
                                   │
                   ┌───────────────▼────────────┐
                   │  Private Subnet            │
                   │  10.0.10.0/24              │
                   └────────────────────────────┘
                                   │
                   ┌───────────────▼────────────┐
                   │  Amazon RDS PostgreSQL     │
                   │                            │
                   │  • Instance: db.t3.medium  │
                   │  • Multi-AZ: Enabled       │
                   │  • Storage: 100 GB SSD     │
                   │  • Automated backups       │
                   │  • Read replicas: 1        │
                   └────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                       Supporting Services                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │ Amazon ECR       │  │ AWS Secrets      │  │ Amazon S3        │     │
│  │ (Docker Images)  │  │ Manager          │  │ (Static Assets)  │     │
│  │                  │  │ • DB credentials │  │ • Logs           │     │
│  │ • fastapi:latest │  │ • JWT secret     │  │ • Backups        │     │
│  │ • nodered:latest │  │ • API keys       │  │ • Reports        │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │ CloudWatch       │  │ X-Ray            │  │ SNS              │     │
│  │ (Monitoring)     │  │ (Tracing)        │  │ (Alerts)         │     │
│  │                  │  │                  │  │                  │     │
│  │ • Logs           │  │ • Performance    │  │ • Email alerts   │     │
│  │ • Metrics        │  │ • Debugging      │  │ • SMS alerts     │     │
│  │ • Alarms         │  │ • Service map    │  │ • PagerDuty      │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Infrastructure as Code (Terraform)

```hcl
# main.tf - High-level infrastructure configuration

# VPC Configuration
resource "aws_vpc" "smart_production" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "smart-production-vpc"
    Environment = "production"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "smart-production-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Fargate Task Definition - FastAPI
resource "aws_ecs_task_definition" "fastapi" {
  family                   = "fastapi-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "2048"  # 2 vCPU
  memory                   = "4096"  # 4 GB
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "fastapi"
      image     = "${aws_ecr_repository.fastapi.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "ALGORITHM"
          value = "HS256"
        },
        {
          name  = "ACCESS_TOKEN_EXPIRE_MINUTES"
          value = "30"
        }
      ]

      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = aws_secretsmanager_secret.db_url.arn
        },
        {
          name      = "SECRET_KEY"
          valueFrom = aws_secretsmanager_secret.jwt_secret.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/fastapi"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/api/v1/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}

# RDS PostgreSQL
resource "aws_db_instance" "postgresql" {
  identifier             = "smart-production-db"
  engine                 = "postgres"
  engine_version         = "16.1"
  instance_class         = "db.t3.medium"
  allocated_storage      = 100
  storage_type           = "gp3"
  storage_encrypted      = true

  db_name  = "smart_production"
  username = "sis4415_user"
  password = random_password.db_password.result

  multi_az               = true
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "smart-production-final-snapshot"

  tags = {
    Name        = "smart-production-db"
    Environment = "production"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "smart-production-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = true
  enable_http2               = true
  enable_cross_zone_load_balancing = true

  tags = {
    Name        = "smart-production-alb"
    Environment = "production"
  }
}

# Auto Scaling
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.fastapi.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  name               = "cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
```

### 7.3 Deployment Pipeline (CI/CD)

```yaml
# .github/workflows/deploy-production.yml

name: Deploy to AWS Production

on:
  push:
    branches:
      - main

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY_FASTAPI: smart-production-fastapi
  ECR_REPOSITORY_NODERED: smart-production-nodered
  ECS_CLUSTER: smart-production-cluster
  ECS_SERVICE_FASTAPI: fastapi-service

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest --cov=api tests/

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build, tag, and push FastAPI image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY_FASTAPI:$IMAGE_TAG \
                       -t $ECR_REGISTRY/$ECR_REPOSITORY_FASTAPI:latest \
                       -f Dockerfile.fastapi .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY_FASTAPI --all-tags

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster ${{ env.ECS_CLUSTER }} \
            --service ${{ env.ECS_SERVICE_FASTAPI }} \
            --force-new-deployment

      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster ${{ env.ECS_CLUSTER }} \
            --services ${{ env.ECS_SERVICE_FASTAPI }}
```

### 7.4 Disaster Recovery Strategy

| Scenario | RTO* | RPO** | Recovery Procedure |
|----------|------|-------|-------------------|
| **Single AZ failure** | 5 min | 0 | Automatic failover to AZ 1b |
| **RDS primary failure** | 2 min | 0 | Automatic failover to Multi-AZ standby |
| **ECS task crash** | 1 min | 0 | Auto-restart via health checks |
| **Complete region failure** | 4 hours | 15 min | Manual failover to us-west-2 (backup region) |
| **Data corruption** | 1 hour | 24 hours | Restore from RDS automated backup |
| **Security breach** | 30 min | 0 | Rotate secrets, deploy new tasks |

*RTO = Recovery Time Objective
**RPO = Recovery Point Objective

---

## 8. Cost Estimation

### 8.1 Monthly AWS Cost Breakdown

#### Compute - ECS Fargate

| Service | Configuration | Hours/Month | Unit Cost | Monthly Cost |
|---------|---------------|-------------|-----------|--------------|
| **FastAPI Tasks** | 2 vCPU, 4 GB RAM | 1440 (2 tasks × 720h) | $0.04048/hour | $58.29 |
| **Node-RED Tasks** | 1 vCPU, 2 GB RAM | 720 (1 task × 720h) | $0.02024/hour | $14.57 |
| **Subtotal** | | | | **$72.86** |

#### Database - RDS PostgreSQL

| Component | Configuration | Monthly Cost |
|-----------|---------------|--------------|
| **Instance** | db.t3.medium (Multi-AZ) | $120.00 |
| **Storage** | 100 GB GP3 SSD | $11.50 |
| **Backup Storage** | 50 GB (7-day retention) | $2.30 |
| **Data Transfer** | 10 GB out | $0.90 |
| **Subtotal** | | **$134.70** |

#### Load Balancing

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **Application Load Balancer** | 1 ALB | $16.20 |
| **LCU Hours** | ~100 LCUs/month | $7.20 |
| **Subtotal** | | **$23.40** |

#### Storage - S3

| Usage | Volume | Monthly Cost |
|-------|--------|--------------|
| **Standard Storage** | 50 GB (logs, backups) | $1.15 |
| **Requests** | 10,000 PUT, 100,000 GET | $0.06 |
| **Data Transfer** | 5 GB out | $0.45 |
| **Subtotal** | | **$1.66** |

#### Container Registry - ECR

| Component | Volume | Monthly Cost |
|-----------|--------|--------------|
| **Storage** | 5 GB (Docker images) | $0.50 |
| **Data Transfer** | 10 GB out | $0.90 |
| **Subtotal** | | **$1.40** |

#### Monitoring and Logging

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **CloudWatch Logs** | 10 GB ingestion, 30-day retention | $5.00 |
| **CloudWatch Metrics** | 50 custom metrics | $1.50 |
| **CloudWatch Alarms** | 10 alarms | $1.00 |
| **X-Ray Tracing** | 100,000 traces | $5.00 |
| **Subtotal** | | **$12.50** |

#### Secrets Management

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **Secrets Manager** | 5 secrets | $2.00 |
| **API calls** | 10,000 calls | $0.40 |
| **Subtotal** | | **$2.40** |

#### Networking

| Component | Configuration | Monthly Cost |
|-----------|---------------|--------------|
| **VPC** | Standard VPC (free) | $0.00 |
| **NAT Gateway** | 1 NAT Gateway | $32.40 |
| **Data Transfer** | 50 GB processed | $2.25 |
| **Subtotal** | | **$34.65** |

---

### 8.2 Total Monthly Cost Summary

| Category | Monthly Cost | Annual Cost |
|----------|-------------|-------------|
| **Compute (Fargate)** | $72.86 | $874.32 |
| **Database (RDS)** | $134.70 | $1,616.40 |
| **Load Balancing** | $23.40 | $280.80 |
| **Storage (S3)** | $1.66 | $19.92 |
| **Container Registry (ECR)** | $1.40 | $16.80 |
| **Monitoring (CloudWatch + X-Ray)** | $12.50 | $150.00 |
| **Secrets Management** | $2.40 | $28.80 |
| **Networking** | $34.65 | $415.80 |
| **TOTAL** | **$283.57** | **$3,402.84** |

### 8.3 Cost Optimization Strategies

#### Immediate Savings (0-3 months)

1. **Reserved Instances for RDS** (-37% on database)
   - Commitment: 1-year partial upfront
   - Savings: ~$50/month
   - New DB cost: $84.70/month

2. **Fargate Spot Instances** (-70% on non-critical tasks)
   - Apply to Node-RED tasks (fault-tolerant)
   - Savings: ~$10/month
   - New compute cost: $62.86/month

3. **S3 Lifecycle Policies**
   - Move logs to Glacier after 30 days
   - Savings: ~$0.50/month

4. **CloudWatch Log Retention**
   - Reduce retention to 7 days (vs. 30)
   - Savings: ~$3/month

**Total Monthly Savings:** ~$63.50
**Optimized Monthly Cost:** **$220.07**

#### Long-term Savings (6-12 months)

1. **Savings Plans for Fargate** (-52% on compute)
   - Commitment: 1-year compute savings plan
   - Additional savings: ~$30/month

2. **Multi-tenant Database**
   - Consolidate dev/staging environments
   - Reduce to 1 RDS instance
   - Savings: ~$120/month (eliminate staging DB)

3. **CloudFront Caching**
   - Cache static GraphQL responses
   - Reduce ALB data transfer
   - Savings: ~$5/month

**Total Optimized Annual Cost:** ~$1,800 (47% reduction)

### 8.4 Scaling Cost Projections

#### Scenario 1: 10x Machine Growth (30 machines)

| Resource | Baseline | 10x Scale | Multiplier |
|----------|----------|-----------|------------|
| Fargate tasks | 2 | 6 | 3x CPU |
| RDS instance | t3.medium | r5.large | 2.5x cost |
| Storage | 100 GB | 500 GB | 5x size |
| **Monthly Cost** | $220 | $580 | 2.6x |

#### Scenario 2: High-frequency Data (1-second intervals)

| Resource | Current (2s) | High-freq (1s) | Impact |
|----------|--------------|----------------|--------|
| Database writes/day | 129,600 | 259,200 | 2x IOPS |
| RDS instance | t3.medium | r5.xlarge | 3x cost |
| Storage growth | 5 GB/month | 10 GB/month | 2x growth |
| **Monthly Cost** | $220 | $420 | 1.9x |

---

## 9. Scalability Strategy

### 9.1 Horizontal Scaling Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      HORIZONTAL SCALING STRATEGY                        │
└─────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────────────┐
                         │  Application Load    │
                         │     Balancer         │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
         ┌──────────▼─────┐  ┌─────▼──────┐  ┌────▼───────┐
         │ ECS Task 1     │  │ ECS Task 2 │  │ ECS Task N │
         │ (FastAPI)      │  │ (FastAPI)  │  │ (FastAPI)  │
         │                │  │            │  │            │
         │ CPU: 40%       │  │ CPU: 45%   │  │ CPU: 35%   │
         └────────┬───────┘  └─────┬──────┘  └────┬───────┘
                  │                │              │
                  └────────────────┼──────────────┘
                                   │
                         ┌─────────▼──────────┐
                         │ RDS PostgreSQL     │
                         │ (Read Replicas)    │
                         │                    │
                         │ Master ──► Replica │
                         └────────────────────┘

Auto-scaling Rules:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IF    avg(CPU) > 70%  for 2 minutes  ──► Scale OUT (+1 task)
IF    avg(CPU) < 30%  for 5 minutes  ──► Scale IN  (-1 task)
IF    requests/sec > 1000             ──► Scale OUT (+2 tasks)
IF    RDS connections > 80%           ──► Add read replica

Limits:
  • Min tasks: 2
  • Max tasks: 10
  • Cooldown: 5 minutes
```

### 9.2 Database Scaling Strategies

#### Read Scaling (Current Implementation)

```
┌───────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Multi-AZ Setup                      │
└───────────────────────────────────────────────────────────────────┘

   ┌──────────────────┐                    ┌──────────────────┐
   │  Primary (AZ-1a) │                    │ Standby (AZ-1b)  │
   │                  │                    │                  │
   │  • All WRITES    │ ──── Sync Rep ───► │  • Hot standby   │
   │  • All READS     │                    │  • Auto-failover │
   └──────────────────┘                    └──────────────────┘
           │
           │ Asynchronous replication
           ▼
   ┌──────────────────┐
   │ Read Replica     │
   │ (Optional)       │
   │                  │
   │  • READ-ONLY     │
   │  • Analytics     │
   │  • Reporting     │
   └──────────────────┘
```

**Read Replica Configuration:**
```sql
-- Application-level read/write splitting
-- Write operations (SQLAlchemy)
engine_write = create_engine(
    "postgresql://user:pass@primary.rds.amazonaws.com:5432/db"
)

-- Read operations (Analytics, Reports)
engine_read = create_engine(
    "postgresql://user:pass@replica.rds.amazonaws.com:5432/db"
)

# Route queries intelligently
@app.get("/machines/stats")
def get_stats(db: Session = Depends(get_read_db)):
    # Uses read replica for analytics
    return db.query(MachineStats24h).all()

@app.post("/machines/data")
def receive_data(db: Session = Depends(get_write_db)):
    # Uses primary for writes
    db.add(new_measurement)
    db.commit()
```

#### Write Scaling (Partitioning Strategy)

```sql
-- Time-series partitioning for measurements table
-- Automatically create monthly partitions

-- Parent table
CREATE TABLE measurements (
    id SERIAL,
    machine_id VARCHAR(20),
    temperature DECIMAL(5,2),
    vibration INTEGER,
    production_count INTEGER,
    fault BOOLEAN,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (timestamp);

-- Partitions (auto-created via cron job)
CREATE TABLE measurements_2025_11
PARTITION OF measurements
FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE measurements_2025_12
PARTITION OF measurements
FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Indexes on each partition
CREATE INDEX idx_measurements_2025_11_machine_timestamp
ON measurements_2025_11(machine_id, timestamp DESC);

-- Query optimizer automatically selects correct partition
SELECT * FROM measurements
WHERE timestamp BETWEEN '2025-11-15' AND '2025-11-20'
  AND machine_id = 'MX-01';
-- Only scans measurements_2025_11 partition
```

**Benefits:**
- Query performance: 10x faster on historical queries
- Maintenance: Drop old partitions instead of DELETE
- Parallelization: Queries scan partitions concurrently

### 9.3 Caching Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CACHING ARCHITECTURE                             │
└─────────────────────────────────────────────────────────────────────────┘

Client
  │
  │ 1. GET /machines/status
  ▼
┌────────────────────┐
│   Redis Cache      │  ← In-memory key-value store
│   (ElastiCache)    │
│                    │
│  Key: "machines:   │  TTL: 2 seconds
│        status:all" │
│                    │
│  Value: [          │
│    {machine_id:..} │
│  ]                 │
└────────┬───────────┘
         │
         │ Cache MISS
         ▼
┌────────────────────┐
│  PostgreSQL DB     │
│                    │
│  SELECT * FROM     │
│  machine_status    │
└────────────────────┘
         │
         │ Store in cache
         └──────────────────────────┐
                                    ▼
                          ┌─────────────────┐
                          │ Update cache    │
                          │ SET key, value  │
                          │ EXPIRE key, 2   │
                          └─────────────────┘

Cache Strategy per Endpoint:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Endpoint                        Cache TTL    Invalidation
──────────────────────────────────────────────────────────
GET /machines                   1 hour       On machine update
GET /machines/status            2 seconds    Write-through
GET /machines/{id}/measurements 30 seconds   Time-based
GraphQL: systemStats            5 seconds    Time-based
GraphQL: machines               1 hour       On machine update
```

**Redis Implementation Example:**
```python
import redis
from functools import wraps

redis_client = redis.Redis(
    host='redis.cache.amazonaws.com',
    port=6379,
    decode_responses=True
)

def cache(ttl=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Try cache first
            cached_value = redis_client.get(cache_key)
            if cached_value:
                return json.loads(cached_value)

            # Cache miss - compute and store
            result = func(*args, **kwargs)
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            return result
        return wrapper
    return decorator

@app.get("/machines/status")
@cache(ttl=2)  # 2-second cache
def get_machines_status(db: Session = Depends(get_db)):
    statuses = db.query(MachineStatus).all()
    return statuses
```

### 9.4 Message Queue Architecture (Future Enhancement)

```
┌─────────────────────────────────────────────────────────────────────────┐
│              ASYNCHRONOUS PROCESSING WITH SQS + Lambda                  │
└─────────────────────────────────────────────────────────────────────────┘

Node-RED                  FastAPI                  SQS Queue
  │                         │                         │
  │ POST /machines/data     │                         │
  ├────────────────────────►│                         │
  │                         │                         │
  │                         │ 1. Quick validation     │
  │                         │ 2. Enqueue message      │
  │                         ├────────────────────────►│
  │                         │                         │
  │ 201 Created             │                         │
  │◄────────────────────────┤                         │
  │                         │                         │
  │                                                   │
  │                                          ┌────────┴────────┐
  │                                          │ Lambda Function │
  │                                          │ (Auto-scaling)  │
  │                                          │                 │
  │                                          │ 1. Dequeue msg  │
  │                                          │ 2. Process data │
  │                                          │ 3. Write to DB  │
  │                                          │ 4. Check alerts │
  │                                          └────────┬────────┘
  │                                                   │
  │                                                   ▼
  │                                          ┌────────────────┐
  │                                          │  PostgreSQL    │
  │                                          │  RDS           │
  │                                          └────────────────┘

Benefits:
  ✓ Decoupled ingestion from processing
  ✓ Handle traffic spikes (1000+ req/s)
  ✓ Retry failed writes automatically
  ✓ Dead-letter queue for anomalies
```

### 9.5 Performance Benchmarks

| Metric | Current (2 tasks) | Scaled (10 tasks) | Target |
|--------|------------------|-------------------|--------|
| **Requests/second** | 500 | 2500 | < 5000 |
| **Avg latency** | 45 ms | 38 ms | < 100 ms |
| **P95 latency** | 120 ms | 95 ms | < 200 ms |
| **P99 latency** | 250 ms | 180 ms | < 500 ms |
| **Database connections** | 20 | 100 | < 200 |
| **CPU utilization** | 35% | 60% | < 70% |
| **Memory utilization** | 45% | 65% | < 80% |
| **Error rate** | 0.01% | 0.01% | < 0.1% |

---

## 10. Monitoring and Observability

### 10.1 CloudWatch Dashboards

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   PRODUCTION MONITORING DASHBOARD                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────┐  ┌───────────────────────────┐          │
│  │  ECS Task Health          │  │  API Latency (ms)         │          │
│  │                           │  │                           │          │
│  │  Running: ████████ 8/10   │  │  150┤                     │          │
│  │  Stopped: ██ 2/10         │  │  100┤    ╱╲  ╱╲           │          │
│  │                           │  │   50┤╱╲╱  ╲╱  ╲╱╲         │          │
│  │  CPU Avg: 62%             │  │    0└────────────────────►│          │
│  │  Memory: 3.1/4.0 GB       │  │       12:00      18:00    │          │
│  └───────────────────────────┘  └───────────────────────────┘          │
│                                                                         │
│  ┌───────────────────────────┐  ┌───────────────────────────┐          │
│  │  Database Performance     │  │  Request Rate (req/s)     │          │
│  │                           │  │                           │          │
│  │  Connections: 85/200      │  │  800┤            ╱╲       │          │
│  │  IOPS: 1250/3000          │  │  600┤      ╱╲   ╱  ╲      │          │
│  │  Storage: 82/100 GB       │  │  400┤  ╱╲╱  ╲╱       ╲    │          │
│  │                           │  │  200┤╱                ╲╱  │          │
│  │  Read Latency: 3.2 ms     │  │    0└────────────────────►│          │
│  │  Write Latency: 8.1 ms    │  │       12:00      18:00    │          │
│  └───────────────────────────┘  └───────────────────────────┘          │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────┐           │
│  │  Active Alerts                                          │           │
│  │                                                          │           │
│  │  🔴 CRITICAL: High database connections (95%)           │           │
│  │  🟡 WARNING: ECS task memory > 80%                      │           │
│  │  🟢 INFO: Auto-scaled to 8 tasks                        │           │
│  └─────────────────────────────────────────────────────────┘           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.2 CloudWatch Alarms Configuration

```python
# cloudwatch_alarms.tf

# Critical: Database CPU > 90%
resource "aws_cloudwatch_metric_alarm" "db_cpu_high" {
  alarm_name          = "smart-production-db-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "90"
  alarm_description   = "Database CPU exceeds 90%"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgresql.id
  }
}

# Critical: ECS Service Unhealthy
resource "aws_cloudwatch_metric_alarm" "ecs_unhealthy_tasks" {
  alarm_name          = "smart-production-ecs-unhealthy"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = "60"
  statistic           = "Average"
  threshold           = "2"
  alarm_description   = "Less than 2 healthy ECS tasks"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "breaching"
}

# Warning: API Latency P99 > 500ms
resource "aws_cloudwatch_metric_alarm" "api_latency_high" {
  alarm_name                = "smart-production-api-latency-p99"
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "2"
  threshold                 = "500"
  alarm_description         = "API P99 latency > 500ms"
  insufficient_data_actions = []
  alarm_actions            = [aws_sns_topic.alerts.arn]

  metric_query {
    id          = "m1"
    return_data = true

    metric {
      metric_name = "TargetResponseTime"
      namespace   = "AWS/ApplicationELB"
      period      = "60"
      stat        = "p99"

      dimensions = {
        LoadBalancer = aws_lb.main.arn_suffix
      }
    }
  }
}
```

### 10.3 Logging Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      STRUCTURED LOGGING FORMAT                          │
└─────────────────────────────────────────────────────────────────────────┘

{
  "timestamp": "2025-11-26T10:30:00.123Z",
  "level": "INFO",
  "service": "fastapi",
  "request_id": "abc123-def456",
  "user_id": "admin",
  "endpoint": "/api/v1/machines/data",
  "method": "POST",
  "status_code": 201,
  "latency_ms": 45,
  "machine_id": "MX-01",
  "message": "Data ingestion successful",
  "trace_id": "1-5f7e8d9a-3b2c1d0e9f8a7b6c5d4e3f2a"
}

Log Aggregation:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source              Destination              Retention
────────────────────────────────────────────────────────────
ECS Container    ──► CloudWatch Logs      ──► 30 days
                 ──► S3 Archive           ──► 1 year
                 ──► ElasticSearch        ──► 7 days

Query Examples (CloudWatch Insights):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Find all errors in last hour
fields @timestamp, level, message, endpoint
| filter level = "ERROR"
| sort @timestamp desc
| limit 100

# Average latency per endpoint
stats avg(latency_ms) by endpoint
| filter @timestamp > ago(1h)

# Top 10 slowest requests
fields @timestamp, endpoint, latency_ms, request_id
| sort latency_ms desc
| limit 10
```

### 10.4 Distributed Tracing (X-Ray)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         X-RAY SERVICE MAP                               │
└─────────────────────────────────────────────────────────────────────────┘

                        ┌──────────────┐
                        │   Client     │
                        └──────┬───────┘
                               │ 450ms
                               ▼
                        ┌──────────────┐
                        │     ALB      │
                        └──────┬───────┘
                               │ 2ms
                               ▼
                        ┌──────────────┐
                        │   FastAPI    │
                        │              │
                        │  Request:    │
                        │  POST /data  │
                        └──────┬───────┘
                               │
                   ┌───────────┼───────────┐
                   │ 5ms       │ 40ms      │ 3ms
                   ▼           ▼           ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │ Validate │ │PostgreSQL│ │  Redis   │
            │ (Pydantic│ │  INSERT  │ │  SETEX   │
            └──────────┘ └──────────┘ └──────────┘

Trace Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trace ID: 1-5f7e8d9a-3b2c1d0e9f8a7b6c5d4e3f2a
Total Duration: 450ms
Status: 200 OK

Segments:
  1. ALB              →  2ms   (HTTP routing)
  2. FastAPI          → 45ms   (Application logic)
     ├─ Validation    →  5ms   (Pydantic schemas)
     ├─ DB Insert     → 40ms   (PostgreSQL write)
     └─ Cache Update  →  3ms   (Redis write)
```

---

## Conclusion

This architecture document provides a comprehensive technical overview of the **Smart Production Line Monitor** system, covering:

- **Scalable microservices architecture** with FastAPI and Node-RED
- **Robust database design** with PostgreSQL featuring triggers, views, and partitioning
- **Secure authentication** using JWT and bcrypt
- **Dual API strategy** with REST and GraphQL for flexibility
- **Production-ready AWS deployment** with multi-AZ redundancy
- **Cost-effective infrastructure** at ~$220/month with optimization strategies
- **Horizontal scalability** supporting 10x growth
- **Comprehensive monitoring** with CloudWatch, X-Ray, and structured logging

The system is designed to handle real-time IoT data ingestion, provide low-latency API access, and scale to support industrial production environments.

---

**Document Version:** 1.0.0
**Last Updated:** November 26, 2025
**Author:** Anibal Simeon Falcon Castro
**License:** Academic Use - Universidad Anáhuac Mayab
