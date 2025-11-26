-- ============================================
-- SMART PRODUCTION LINE - DATABASE SCHEMA
-- Project: SIS4415 Final Project - Option A
-- Author: Anibal Simeon Falcon Castro
-- ============================================

-- Tabla de usuarios (para JWT authentication)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de máquinas (catálogo)
CREATE TABLE machines (
    id SERIAL PRIMARY KEY,
    machine_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de mediciones históricas
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

-- Índice para consultas rápidas por máquina y timestamp
CREATE INDEX idx_measurements_machine_timestamp 
ON measurements(machine_id, timestamp DESC);

-- Tabla de estado actual de máquinas (optimización)
CREATE TABLE machine_status (
    machine_id VARCHAR(20) PRIMARY KEY REFERENCES machines(machine_id) ON DELETE CASCADE,
    temperature DECIMAL(5,2),
    vibration INTEGER,
    production_count INTEGER,
    fault BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP NOT NULL
);

-- Tabla de alertas
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

-- Índice para alertas no resueltas
CREATE INDEX idx_alerts_unresolved 
ON alerts(resolved, created_at DESC) WHERE resolved = FALSE;

-- ============================================
-- DATOS INICIALES
-- ============================================

-- Insertar máquinas de ejemplo
INSERT INTO machines (machine_id, name, location, status) VALUES
('MX-01', 'Assembly Line Alpha', 'Building A - Floor 1', 'active'),
('MX-02', 'Welding Station Beta', 'Building A - Floor 2', 'active'),
('MX-03', 'Quality Control Gamma', 'Building B - Floor 1', 'active');

-- Insertar estado inicial de máquinas
INSERT INTO machine_status (machine_id, temperature, vibration, production_count, fault, last_updated) VALUES
('MX-01', 65.0, 20, 0, FALSE, CURRENT_TIMESTAMP),
('MX-02', 72.0, 25, 0, FALSE, CURRENT_TIMESTAMP),
('MX-03', 68.0, 18, 0, FALSE, CURRENT_TIMESTAMP);

-- Usuario de prueba (password será hasheado en el backend)
-- Placeholder temporal
INSERT INTO users (username, email, password_hash) VALUES
('admin', 'admin@smartproduction.com', 'placeholder_will_be_updated');

-- ============================================
-- VISTAS ÚTILES (para reportes en Node-RED)
-- ============================================

-- Vista: estadísticas últimas 24 horas por máquina
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

-- Vista: alertas activas
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

-- Vista: resumen general del sistema
CREATE VIEW system_overview AS
SELECT 
    (SELECT COUNT(*) FROM machines WHERE status = 'active') as active_machines,
    (SELECT COUNT(*) FROM machines) as total_machines,
    (SELECT COUNT(*) FROM alerts WHERE resolved = FALSE) as active_alerts,
    (SELECT SUM(production_count) FROM machine_status) as current_total_production,
    (SELECT AVG(temperature) FROM machine_status) as avg_system_temperature,
    (SELECT MAX(vibration) FROM machine_status) as max_system_vibration;

-- ============================================
-- FUNCIONES ÚTILES
-- ============================================

-- Función para limpiar mediciones antiguas (más de 30 días)
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

-- Función para generar alerta automática
CREATE OR REPLACE FUNCTION check_and_create_alert()
RETURNS TRIGGER AS $$
BEGIN
    -- Alerta de temperatura alta
    IF NEW.temperature > 90 THEN
        INSERT INTO alerts (machine_id, alert_type, severity, message)
        VALUES (NEW.machine_id, 'high_temperature', 'critical', 
                'Temperature exceeded 90°C: ' || NEW.temperature || '°C');
    END IF;
    
    -- Alerta de vibración alta
    IF NEW.vibration > 80 THEN
        INSERT INTO alerts (machine_id, alert_type, severity, message)
        VALUES (NEW.machine_id, 'high_vibration', 'high', 
                'Vibration exceeded safe threshold: ' || NEW.vibration);
    END IF;
    
    -- Alerta de falla
    IF NEW.fault = TRUE THEN
        INSERT INTO alerts (machine_id, alert_type, severity, message)
        VALUES (NEW.machine_id, 'machine_fault', 'critical', 
                'Machine reported a fault condition');
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para alertas automáticas en nuevas mediciones
CREATE TRIGGER trigger_alert_on_measurement
AFTER INSERT ON measurements
FOR EACH ROW
EXECUTE FUNCTION check_and_create_alert();

-- ============================================
-- GRANT PERMISSIONS
-- ============================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sis4415_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sis4415_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO sis4415_user;