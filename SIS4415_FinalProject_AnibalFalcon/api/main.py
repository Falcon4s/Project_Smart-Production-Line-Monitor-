from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from api.config import settings
from api.routes import auth, machines, health
from api.graphql.schema import schema

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
    description="Smart Production Line Monitor API"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas REST
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(machines.router, prefix=settings.API_V1_PREFIX)

# Registrar GraphQL
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "message": "Smart Production Line Monitor API",
        "version": "1.0.0",
        "docs": "/docs",
        "graphql": "/graphql",
        "health": f"{settings.API_V1_PREFIX}/health"
    }