from fastapi import FastAPI
from routes import postgres_routes, neo4j_routes

app = FastAPI(title="Asset API")

# Include routes
app.include_router(postgres_routes.router, prefix="/postgres")
app.include_router(neo4j_routes.router, prefix="/neo4j")

@app.get("/")
def home():
    return {"status": "running"}