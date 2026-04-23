# Payment Reconciliation Service (Pine Labs Assessment)

## Overview

This project is a lightweight backend service built using FastAPI to handle payment lifecycle events and provide reconciliation insights.

The system is designed to:

- ingest payment events from multiple systems
- maintain transaction and merchant state
- expose APIs for operational visibility
- identify discrepancies between payment and settlement states

---

## Architecture Overview

The system follows a layered architecture:

```bash
app/
├── api/       # API layer (routes)
├── core/      # config, database
├── models/    # SQLAlchemy models
├── schemas/   # Pydantic schemas
├── utils/     # helpers (state machine)
```

### Key Components

- **FastAPI** – API framework
- **SQLAlchemy (Async)** – ORM layer
- **SQLite** – Light Weight SQL Database
- **httpx** – async HTTP client (testing & ingestion)
- **pytest** – testing framework

---

## Design Decisions

### 1. Event-Driven Architecture
Each incoming event updates transaction state while preserving full event history.

---

### 2. Idempotency Handling
- Enforced via unique constraint on `event_id`
- Duplicate events are safely ignored
- Prevents state corruption

---

### 3. State Management
Transaction status is derived using a controlled state transition logic.

Example flow:

**payment_initiated → payment_processed → settled**

---

### 4. Database Design

Entities:
- **Merchants**
- **Transactions**
- **Events (event history)**

Designed to:
- support efficient filtering
- enable SQL-based aggregation
- avoid Python-side data processing

---

### 5. Reconciliation Logic

Discrepancies are detected using SQL queries:

- processed but not settled
- failed but settled
- inconsistent event sequences

---

### 6. Bulk Ingestion Strategy

- Batched async requests
- Controlled concurrency
- Throttling to avoid DB overload

---


## Assumptions & Tradeoffs

- **SQLite over PostgreSQL**  
  Chosen for simplicity and easy setup. Tradeoff is limited write concurrency. Can be replaced with PostgreSQL for production.

- **Synchronous event processing**  
  Keeps implementation simple but may not scale under high load. Can be improved using message queues.

- **Idempotency via event_id constraint**  
  Ensures duplicate events don’t corrupt state. Limited to single-system guarantees.

- **Startup-based schema creation**  
  Quick for development but not suitable for production. Migrations (Alembic) would be preferred.

- **No authentication layer**  
  Out of scope for this assignment. Can be added with JWT-based auth in production.


## Key Highlights

- Idempotent event ingestion
- SQL-based reconciliation logic (no Python loops)
- Async-safe architecture
- Clean API design with filtering, pagination, sorting
- Bulk ingestion with batching and throttling
- Comprehensive test coverage
- Basic indexing is added on frequently queried fields (merchant_id, status, created_at) to improve query performance.

---

## Setup Instructions (On Local)

### 1. Clone Repository

```bash
git clone https://github.com/YashwanthSimhaa/pine-labs-assessment.git
cd pine-labs-assessment
```

### 2. Create and activate Python Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup `.env`
```bash
1. Create a new file named `.env` under root(/pine-labs-assessment/) directory.
2. Copy the content of `.env.example` to `.env`.
3. Update the values in `.env` file  with your details.
```

### 5. Start the Server
```bash
python run.py
```
or 
```bash
uvicorn app.main:app
```

### 6. Access API Docs
```bash
http://localhost:8000/docs
```

## API Endpoints

### 1. Ingest Events
POST /api/v1/events

### 2. List Transactions
GET /api/v1/transactions

### 3. Transaction Details
GET /api/v1/transactions/{transaction_id}

### 4. Reconciliation Summary
GET /api/v1/reconciliation/summary

### 5. Reconciliation Discrepancies
GET /api/v1/reconciliation/discrepancies

---

## Testing

Run tests:
```bash
pytest -v
```

### Loading Sample Data
A dataset with ~10,000 events is used.

Load Data
```bash
python -m scripts.load_sample_data
```

Features:

- batched ingestion
- retry-safe requests
- logging for failures


## Postman Collection

A Postman collection is included in the repository along with environment:
```bash
postman/
├── PineLabs_Assessment_APIs.postman_collection.json
└── PineLabs_Env.postman_environment.json
```

### How to use:

1. Open Postman
2. Click **Import**
3. Import both files into Postman
4. Select the environment (`PineLabs Env`)
5. Run APIs directly

---

## Deployment

The application is also deployed on Railway:

https://web-production-a8565.up.railway.app/docs

Note:
SQLite is used for simplicity. Railway filesystem is ephemeral, so data may reset between deployments.

