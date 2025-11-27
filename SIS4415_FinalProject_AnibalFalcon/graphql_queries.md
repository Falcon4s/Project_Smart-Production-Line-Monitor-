# GraphQL Queries - Smart Production Line Monitor

This document contains the GraphQL queries, mutations, and subscriptions implemented for the SIS4415 final project.

---

## Table of Contents

1. [Queries](#queries)
   - Get All Machines
   - Get Machine Measurements
   - Get All Machine Statuses
2. [Mutations](#mutations)
   - Create Machine
   - Add Measurement
3. [Subscriptions](#subscriptions)
   - Watch Machine Updates

---

## Queries

### 1. Get All Machines

**Description:** Retrieves complete information about all registered machines in the system.

**Usage:** Display machine catalog with details.
```graphql
query GetAllMachines {
  machines {
    id
    machineId
    name
    location
    status
    createdAt
  }
}
```

**Expected Result:**
```json
{
  "data": {
    "machines": [
      {
        "id": 1,
        "machineId": "MX-01",
        "name": "Assembly Line 1",
        "location": "Building A",
        "status": "active",
        "createdAt": "2025-11-27T10:00:00"
      },
      {
        "id": 2,
        "machineId": "MX-02",
        "name": "Assembly Line 2",
        "location": "Building A",
        "status": "active",
        "createdAt": "2025-11-27T10:00:00"
      },
      {
        "id": 3,
        "machineId": "MX-03",
        "name": "Assembly Line 3",
        "location": "Building B",
        "status": "active",
        "createdAt": "2025-11-27T10:00:00"
      }
    ]
  }
}
```

---

### 2. Get Machine Measurements

**Description:** Retrieves historical measurement data for a specific machine with configurable limit.

**Usage:** Display telemetry history and trends for analysis.
```graphql
query GetMachineMeasurements {
  measurements(machineId: "MX-01", limit: 10) {
    id
    machineId
    temperature
    vibration
    productionCount
    fault
    timestamp
  }
}
```

**Parameters:**
- `machineId` (String, optional): Filter by specific machine (e.g., "MX-01")
- `limit` (Int, optional, default: 100): Maximum number of records to return

**Expected Result:**
```json
{
  "data": {
    "measurements": [
      {
        "id": 1523,
        "machineId": "MX-01",
        "temperature": 68.5,
        "vibration": 22,
        "productionCount": 15,
        "fault": false,
        "timestamp": "2025-11-27T14:30:45"
      },
      {
        "id": 1522,
        "machineId": "MX-01",
        "temperature": 70.2,
        "vibration": 18,
        "productionCount": 17,
        "fault": false,
        "timestamp": "2025-11-27T14:30:43"
      }
    ]
  }
}
```

---

### 3. Get All Machine Statuses

**Description:** Retrieves the current operational state snapshot for all machines.

**Usage:** Display real-time system overview dashboard.
```graphql
query GetAllMachineStatuses {
  allMachineStatuses {
    machineId
    temperature
    vibration
    productionCount
    fault
    lastUpdated
  }
}
```

**Expected Result:**
```json
{
  "data": {
    "allMachineStatuses": [
      {
        "machineId": "MX-01",
        "temperature": 65.8,
        "vibration": 20,
        "productionCount": 14,
        "fault": false,
        "lastUpdated": "2025-11-27T14:32:10"
      },
      {
        "machineId": "MX-02",
        "temperature": 72.3,
        "vibration": 25,
        "productionCount": 18,
        "fault": false,
        "lastUpdated": "2025-11-27T14:32:10"
      },
      {
        "machineId": "MX-03",
        "temperature": 68.1,
        "vibration": 17,
        "productionCount": 16,
        "fault": false,
        "lastUpdated": "2025-11-27T14:32:10"
      }
    ]
  }
}
```

---

## Mutations

### 4. Create Machine

**Description:** Registers a new machine in the system.

**Usage:** Add new equipment to the monitoring system.
```graphql
mutation CreateMachine {
  createMachine(machineInput: {
    machineId: "MX-04"
    name: "Assembly Line 4"
    location: "Building B"
    status: "active"
  }) {
    id
    machineId
    name
    location
    status
    createdAt
  }
}
```

**Input Parameters:**
- `machineId` (String, required): Unique machine identifier
- `name` (String, required): Machine display name
- `location` (String, optional): Physical location
- `status` (String, optional, default: "active"): Operational status

**Expected Result:**
```json
{
  "data": {
    "createMachine": {
      "id": 4,
      "machineId": "MX-04",
      "name": "Assembly Line 4",
      "location": "Building B",
      "status": "active",
      "createdAt": "2025-11-27T14:35:00"
    }
  }
}
```

---

### 5. Add Measurement

**Description:** Manually insert a telemetry measurement into the system.

**Usage:** Test data ingestion or insert historical data.
```graphql
mutation AddMeasurement {
  addMeasurement(measurementInput: {
    machineId: "MX-01"
    temperature: 75.5
    vibration: 30
    productionCount: 18
    fault: false
    timestamp: "2025-11-27T10:00:00Z"
  }) {
    id
    machineId
    temperature
    vibration
    productionCount
    fault
    timestamp
  }
}
```

**Input Parameters:**
- `machineId` (String, required): Target machine identifier
- `temperature` (Float, optional): Temperature in Celsius
- `vibration` (Int, optional): Vibration level (0-100)
- `productionCount` (Int, optional): Units produced per minute
- `fault` (Boolean, optional, default: false): Fault flag
- `timestamp` (DateTime, optional): Measurement timestamp (defaults to current time)

**Expected Result:**
```json
{
  "data": {
    "addMeasurement": {
      "id": 1524,
      "machineId": "MX-01",
      "temperature": 75.5,
      "vibration": 30,
      "productionCount": 18,
      "fault": false,
      "timestamp": "2025-11-27T10:00:00"
    }
  }
}
```

---

## Subscriptions

### 6. Watch Machine Updates

**Description:** Real-time subscription that streams machine status updates every 2 seconds.

**Usage:** Monitor live production line data with WebSocket connection.

**Watch All Machines:**
```graphql
subscription WatchAllMachines {
  machineUpdates {
    machineId
    temperature
    vibration
    productionCount
    fault
    lastUpdated
  }
}
```

**Watch Specific Machine:**
```graphql
subscription WatchMX01 {
  machineUpdates(machineId: "MX-01") {
    machineId
    temperature
    vibration
    productionCount
    fault
    lastUpdated
  }
}
```

**Parameters:**
- `machineId` (String, optional): Filter updates for specific machine

**Expected Result (continuous stream):**
```json
{
  "data": {
    "machineUpdates": {
      "machineId": "MX-01",
      "temperature": 67.2,
      "vibration": 23,
      "productionCount": 16,
      "fault": false,
      "lastUpdated": "2025-11-27T14:40:12"
    }
  }
}
```

**Note:** This subscription continuously emits data every 2 seconds. Values will change in real-time as the Node-RED simulator sends new telemetry data to the backend.

---

## How to Test

### Using GraphQL Playground

1. Open http://localhost:8000/graphql in your browser
2. Copy any query/mutation from above into the left panel
3. Click the "Play" button (▶) to execute
4. View results in the right panel

### Testing Subscriptions

**Requirements:**
- WebSocket-capable GraphQL client (GraphQL Playground supports this)

**Steps:**
1. Paste subscription query into GraphQL Playground
2. Click "Play" button (▶)
3. Ensure Node-RED simulator is running (Production Line toggle ON)
4. Watch data stream update every 2 seconds
5. Click "Stop" (■) to end subscription

### Authentication

**Note:** GraphQL endpoint is currently public for demonstration purposes. In production, add JWT authentication:
```graphql
# HTTP Headers
{
  "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"
}
```

---

## Integration with Node-RED Dashboard

The GraphQL API complements the REST API used by the Node-RED dashboard:

- **Dashboard uses:** REST API (POST /api/machines/data, GET /api/machines/status)
- **GraphQL provides:** Alternative query interface with subscriptions for real-time updates
- **Use case:** External applications can use GraphQL subscriptions to monitor production without polling

---

## Error Handling

### Common Errors

**Machine Not Found:**
```json
{
  "errors": [
    {
      "message": "Machine with ID 'MX-99' not found",
      "path": ["machine"]
    }
  ]
}
```

**Invalid Input:**
```json
{
  "errors": [
    {
      "message": "Field 'machineId' of required type 'String!' was not provided",
      "path": ["createMachine"]
    }
  ]
}
```

**Database Connection Error:**
```json
{
  "errors": [
    {
      "message": "Database connection failed",
      "path": ["measurements"]
    }
  ]
}
```

---

## Additional Resources

- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Architecture:** See `architecture.md` for system design
- **REST Endpoints:** See `README.md` for REST API reference

---

## Author

**Anibal Simeon Falcon Castro**  
Universidad Anáhuac Mayab  
SIS4415 - Information Technology in the Fourth Industrial Revolution  
November 2025