# Docker Setup - Smart Production Line Monitor

This directory contains the Docker configuration for the SIS4415 project.

## Quick Start

### Start services
```bash
docker-compose up -d
```

### Verify services are running
```bash
docker-compose ps
```

### View logs
```bash
docker-compose logs -f postgres
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (WARNING: deletes all data)
```bash
docker-compose down -v
```

## Connect to Database

### From DataGrip
- **Host:** `localhost`
- **Port:** `5432`
- **Database:** `smart_production`
- **User:** `sis4415_user`
- **Password:** `production2025`

### From terminal (psql)
```bash
docker exec -it sis4415-postgres psql -U sis4415_user -d smart_production
```

## Database Structure

### Main tables
- `users` - System users
- `machines` - Machine catalog
- `measurements` - Historical measurements
- `machine_status` - Current state of each machine
- `alerts` - Alert system

### Views
- `machine_stats_24h` - Statistics for last 24 hours
- `active_alerts` - Unresolved alerts
- `system_overview` - System overview

### Functions
- `cleanup_old_measurements()` - Cleans old data
- `check_and_create_alert()` - Generates automatic alerts

## Environment Variables

Edit the `.env` file to change credentials:
```env
POSTGRES_USER=sis4415_user
POSTGRES_PASSWORD=production2025
POSTGRES_DB=smart_production
POSTGRES_PORT=5432
```

## Useful Commands

### Reset database
```bash
docker-compose down -v
docker-compose up -d
```

### Create backup
```bash
docker exec sis4415-postgres pg_dump -U sis4415_user smart_production > backup.sql
```

### Restore backup
```bash
docker exec -i sis4415-postgres psql -U sis4415_user smart_production < backup.sql
```

### Execute queries directly
```bash
docker exec -it sis4415-postgres psql -U sis4415_user -d smart_production -c "SELECT * FROM machines;"
```

## Security

WARNING: The credentials in this project are only for local development.
In production, use secure environment variables and never commit credentials.

## Volumes

Data is persisted in the Docker volume `postgres_data`.
To delete all data: `docker-compose down -v`

---

**Project:** SIS4415 - Smart Production Line Monitor
**Author:** Anibal Simeon Falcon Castro
**Option:** A
