# 🧠 Asset Management Data Platform

A modular, real-time system for generating, processing, enriching, and serving asset management data using microservices, streaming, graph databases, and APIs.

---

## 📐 Architecture Overview

┌────────────┐ ┌──────────────┐ ┌────────────┐
│ Producer │ ───▶ │ Kafka │ ──▶ │ Spark │
└────────────┘ └──────────────┘ └────────────┘
│
┌───────────────┴──────────────┐
│ │
┌────▼─────┐ ┌──────▼───────┐
│PostgreSQL│ │ Neo4j │
└────▲─────┘ └──────▲───────┘
│ │
│ ┌────────────┐ │
└────────▶│ FastAPI │◀──────┘
└────────────┘

yaml
Copy
Edit

---

## ⚙️ Technologies Used

| Layer        | Tool/Service       | Purpose                                    |
|--------------|--------------------|--------------------------------------------|
| Streaming    | **Kafka**          | Message bus for FX, stock, and portfolio events |
| Processing   | **PySpark**        | Structured streaming, enrichment, analytics |
| Storage      | **PostgreSQL**     | Tabular data storage (trades, FX, etc.)    |
| Graph DB     | **Neo4j**          | Relationship modeling (traders, portfolios)|
| API          | **FastAPI**        | Serving queries, training, predictions     |
| DevOps       | **Docker Compose** | Local orchestration                        |

---

## 📂 Folder Structure


---

## 🚀 Running the Project Locally

1. **Build and start all services**:

```bash
docker-compose up --build
FastAPI is available at:
📡 http://localhost:8000/docs

Kafka UI / topics:
Consider adding a UI like kafka-ui or kafdrop (optional)

Neo4j browser:
🌐 http://localhost:7474
Login: neo4j / test

🧪 FastAPI Endpoints
🔄 PostgreSQL
Endpoint	Description
GET /postgres/trades	List recent trades

🔗 Neo4j
Endpoint	Description
GET /neo4j/relationships	Show trader → portfolio → asset
POST /neo4j/train	Train model using graph data

📦 Data Model
🏦 PostgreSQL Tables (example)
trades → Stock/FX trades

portfolios → Valuations per account

fx_rates → Time-stamped FX rates

🔗 Neo4j Graph (example)
ruby
Copy
Edit
(:Trader)-[:MANAGES]->(:Portfolio)-[:OWNS]->(:Asset)
📈 Model Training Options
Use PostgreSQL to train time-series or tabular models (e.g. XGBoost)

Use Neo4j for graph-based ML (fraud, risk, influence detection)

Expose /train and /predict endpoints for API-triggered training
