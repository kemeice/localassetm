from fastapi import APIRouter
from neo4j import GraphDatabase

router = APIRouter()

NEO4J_URI = "bolt://neo4j:7687"
driver = GraphDatabase.driver(NEO4J_URI, auth=("neo4j", "test"))

@router.get("/relationships")
def get_portfolio_relationships():
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Trader)-[:MANAGES]->(p:Portfolio)-[:OWNS]->(a:Asset)
            RETURN t.name AS trader, p.id AS portfolio, a.symbol AS asset
        """)
        return [r.data() for r in result]

@router.post("/train")
def train_model():
    # Example: Count unique traders/portfolios (stub)
    with driver.session() as session:
        count = session.run("MATCH (t:Trader) RETURN count(t) AS total").single()["total"]
    return {"model": "GraphModel_v1", "status": "trained", "entities": count}