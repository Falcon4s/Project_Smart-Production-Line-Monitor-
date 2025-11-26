# Docker Setup - Smart Production Line Monitor

Este directorio contiene la configuración Docker para el proyecto SIS4415.

## 🚀 Inicio Rápido

### Levantar los servicios
```bash
docker-compose up -d
```

### Verificar que estén corriendo
```bash
docker-compose ps
```

### Ver logs
```bash
docker-compose logs -f postgres
```

### Detener los servicios
```bash
docker-compose down
```

### Detener y eliminar volúmenes (⚠️ elimina todos los datos)
```bash
docker-compose down -v
```

## 📊 Conectar a la Base de Datos

### Desde DataGrip
- **Host:** `localhost`
- **Port:** `5432`
- **Database:** `smart_production`
- **User:** `sis4415_user`
- **Password:** `production2025`

### Desde terminal (psql)
```bash
docker exec -it sis4415-postgres psql -U sis4415_user -d smart_production
```

## 🗄️ Estructura de Base de Datos

### Tablas principales
- `users` - Usuarios del sistema
- `machines` - Catálogo de máquinas
- `measurements` - Mediciones históricas
- `machine_status` - Estado actual de cada máquina
- `alerts` - Sistema de alertas

### Vistas
- `machine_stats_24h` - Estadísticas últimas 24 horas
- `active_alerts` - Alertas sin resolver
- `system_overview` - Resumen general del sistema

### Funciones
- `cleanup_old_measurements()` - Limpia datos antiguos
- `check_and_create_alert()` - Genera alertas automáticas

## 📝 Variables de Entorno

Edita el archivo `.env` para cambiar las credenciales:
```env
POSTGRES_USER=sis4415_user
POSTGRES_PASSWORD=production2025
POSTGRES_DB=smart_production
POSTGRES_PORT=5432
```

## ⚙️ Comandos Útiles

### Resetear la base de datos
```bash
docker-compose down -v
docker-compose up -d
```

### Hacer backup
```bash
docker exec sis4415-postgres pg_dump -U sis4415_user smart_production > backup.sql
```

### Restaurar backup
```bash
docker exec -i sis4415-postgres psql -U sis4415_user smart_production < backup.sql
```

### Ejecutar queries directamente
```bash
docker exec -it sis4415-postgres psql -U sis4415_user -d smart_production -c "SELECT * FROM machines;"
```

## 🔒 Seguridad

⚠️ **IMPORTANTE:** Las credenciales en este proyecto son solo para desarrollo local.
En producción, usa variables de entorno seguras y nunca commitees credenciales.

## 📦 Volúmenes

Los datos se persisten en el volumen Docker `postgres_data`. 
Para eliminar todos los datos: `docker-compose down -v`

---

**Proyecto:** SIS4415 - Smart Production Line Monitor  
**Autor:** Anibal Simeon Falcon Castro  
**Opción:** A