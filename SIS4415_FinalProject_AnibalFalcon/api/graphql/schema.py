import strawberry
from typing import List, Optional, AsyncGenerator
import asyncio

from api.graphql.types import (
    MachineType,
    MeasurementType,
    MachineStatusType,
    MachineInput,
    MeasurementInput
)
from api.graphql import resolvers


@strawberry.type
class Query:
    machines: List[MachineType] = strawberry.field(resolver=resolvers.get_machines)
    machine: Optional[MachineType] = strawberry.field(resolver=resolvers.get_machine_by_id)
    measurements: List[MeasurementType] = strawberry.field(resolver=resolvers.get_measurements)
    machine_status: Optional[MachineStatusType] = strawberry.field(resolver=resolvers.get_machine_status)
    all_machine_statuses: List[MachineStatusType] = strawberry.field(resolver=resolvers.get_all_machine_statuses)


@strawberry.type
class Mutation:
    create_machine: MachineType = strawberry.field(resolver=resolvers.create_machine)
    add_measurement: MeasurementType = strawberry.field(resolver=resolvers.add_measurement)


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def machine_updates(
        self, 
        machine_id: Optional[str] = None
    ) -> AsyncGenerator[MachineStatusType, None]:
        """Subscribe to real-time machine updates from database"""
        from api.database import SessionLocal
        from api.models.machine import MachineStatus
        
        while True:
            # Crear sesión de base de datos
            db = SessionLocal()
            try:
                # Query para obtener estado actual de las máquinas
                query = db.query(MachineStatus)
                
                # Si se especifica machine_id, filtrar por esa máquina
                if machine_id:
                    query = query.filter(MachineStatus.machine_id == machine_id)
                
                # Obtener todos los estados
                statuses = query.all()
                
                # Emitir actualización para cada máquina
                for status in statuses:
                    yield MachineStatusType(
                        machine_id=status.machine_id,
                        temperature=float(status.temperature) if status.temperature else 0.0,
                        vibration=int(status.vibration) if status.vibration else 0,
                        production_count=int(status.production_count) if status.production_count else 0,
                        fault=status.fault,
                        last_updated=status.last_updated
                    )
            finally:
                db.close()
            
            # Esperar 2 segundos antes de la siguiente actualización
            # (coincide con la frecuencia del simulador)
            await asyncio.sleep(2)


schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)