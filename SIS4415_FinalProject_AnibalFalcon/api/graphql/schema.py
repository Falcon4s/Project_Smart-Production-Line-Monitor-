import strawberry
from typing import List, Optional
from api.graphql.types import (
    MachineType,
    MeasurementType,
    MachineStatusType,
    AlertType,
    SystemStatsType
)
from api.graphql import resolvers


@strawberry.type
class Query:
    machines: List[MachineType] = strawberry.field(resolver=resolvers.get_machines)
    machine: Optional[MachineType] = strawberry.field(resolver=resolvers.get_machine)
    machines_status: List[MachineStatusType] = strawberry.field(resolver=resolvers.get_machines_status)
    measurements: List[MeasurementType] = strawberry.field(resolver=resolvers.get_measurements)
    alerts: List[AlertType] = strawberry.field(resolver=resolvers.get_alerts)
    system_stats: SystemStatsType = strawberry.field(resolver=resolvers.get_system_stats)


@strawberry.type
class Subscription:
    live_machine_data: List[MachineStatusType] = strawberry.subscription(resolver=resolvers.live_machine_data)
    live_alerts: List[AlertType] = strawberry.subscription(resolver=resolvers.live_alerts)


# Crear el schema
schema = strawberry.Schema(query=Query, subscription=Subscription)