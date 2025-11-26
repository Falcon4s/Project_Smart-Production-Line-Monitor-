# GraphQL Queries - Smart Production Line Monitor

This file contains the essential GraphQL queries for project demonstration.

---

## 1. GetSystemOverview

**Description:** Retrieves a complete system view with machines, current states, and general statistics.

**Usage:** Main query to display system status.
```graphql
query GetSystemOverview {
  machines {
    machineId
    name
    status
  }
  machinesStatus {
    machineId
    temperature
    vibration
    productionCount
    fault
  }
  systemStats {
    totalMachines
    activeMachines
    totalMeasurements
    activeAlerts
  }
}
```

**Expected result:**
- List of 3 machines (MX-01, MX-02, MX-03)
- Current state of each machine with metrics
- Complete system statistics

---

## 2. GetRecentMeasurements

**Description:** Retrieves the last 10 historical measurements from all machines.

**Usage:** Display captured data history.
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

**Expected result:**
- Last 10 measurements ordered by timestamp
- Data from the 3 machines mixed

---

## 3. LiveMachineData (Subscription)

**Description:** Real-time subscription that updates machine state every 2 seconds.

**Usage:** Demonstrate real-time data capability with WebSockets.
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

**Expected result:**
- Continuous data stream
- Updates every 2 seconds
- Changing values of temperature, vibration, and production

---

## Additional Queries (Optional)

### GetSingleMachine
```graphql
query GetSingleMachine {
  machine(machineId: "MX-01") {
    machineId
    name
    location
    status
  }
}
```

### GetActiveAlerts
```graphql
query GetActiveAlerts {
  alerts(resolved: false) {
    machineId
    alertType
    severity
    message
    createdAt
  }
}
