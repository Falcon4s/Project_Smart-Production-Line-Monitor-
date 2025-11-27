from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from api.routes import auth, machines, alerts, health
from api.graphql.schema import schema

app = FastAPI(
    title="Smart Production Line Monitor API",
    description="REST and GraphQL API for IoT Manufacturing System",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# REST API endpoints
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(machines.router, prefix="/api/machines", tags=["Machines"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(health.router, prefix="/api/health", tags=["Health"])


@app.get("/")
async def root():
    return {
        "message": "Smart Production Line Monitor API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "graphql": "/graphql",
            "health": "/api/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)