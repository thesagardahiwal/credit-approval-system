# Credit Approval System 💳

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.0-green?style=for-the-badge&logo=django)
![Celery](https://img.shields.io/badge/Celery-5.3-lemon?style=for-the-badge&logo=celery)
![Redis](https://img.shields.io/badge/Redis-7.0-red?style=for-the-badge&logo=redis)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-24.0-blue?style=for-the-badge&logo=docker)

A robust, production-grade backend for managing customer credit limits, processing loan applications, and assessing eligibility based on diverse financial metrics. Built with **separation of concerns** and **scalability** in mind.

---

## 🏗️ Architecture

The project follows a **Domain-Driven Design (DDD)** inspired structure, decoupling business logic from the framework (`views.py` / `models.py`).

```text
apps/
├── customers/       # Domain: Customer Profile & Limits
│   ├── services/    # Business Logic (e.g., limit calculation)
│   └── ...
├── loans/           # Domain: Loan Lifecycle & Risk
│   ├── services/    # Pure Logic
│   │   ├── credit_score.py  # Pluggable Scoring Engine
│   │   ├── interest.py      # Compound Interest Calc
│   │   └── loan_service.py  # Orchestrator
│   └── ...
└── ingestion/       # Domain: Data Pipeline
    ├── loaders.py   # Bulk Data Processors
    └── tasks.py     # Celery Async Workers
```

### Key Components
1.  **Service Layer**: All business logic (e.g., Credit Score, Eligibility) resides in `services/`, making it unit-testable and framework-independent.
2.  **Async Ingestion**: Large Excel files are processed in background using **Celery** to prevent blocking the main thread.
3.  **Dockerized**: Fully containerized environment with `web`, `worker`, `db`, and `redis` services.

---

## 🚀 Setup & Running

1.  **Start Services**:
    ```bash
    docker-compose up --build
    ```
2.  **Ingest Data** (Async Trigger):
    ```bash
    docker-compose run web python manage.py shell
    # >>> from apps.ingestion.tasks import ingest_customer_data
    # >>> ingest_customer_data.delay('customer_data.xlsx')
    ```
3.  **Run Tests**:
    ```bash
    docker-compose run web python manage.py test
    ```

---

## 🧠 Design Decisions & Trade-offs

### 1. Robust Ingestion Flow
*   **Decision**: Used `pandas` with chunking and row-level validation.
*   **Why?**: To handle large datasets without OOM errors.
*   **Trade-off**: Slightly slower than raw SQL COPY, but allows application-level validation logic (e.g., checking foreign keys).

### 2. Credit Score Algorithm
*   **Decision**: Implemented a **transparent, weighted scoring model** (0-100) based on repayment history (35%), volume (25%), count (20%), and activity (20%).
*   **Why?**: Opaque algorithms frustrate users. A component-based score allows showing users *why* they were rejected.
*   **Trade-off**: Simple heuristics might miss complex risk factors (e.g., macroeconomic trends) which ML models could catch.

### 3. Separation of Concerns
*   **Decision**: Business logic is strictly kept out of Views and Models.
*   **Why?**: `views.py` should only handle HTTP concerns (request parsing, response formatting). `models.py` should only handle DB schema.
*   **Benefit**: We can switch from HTTP to gRPC or CLI without rewriting business logic.

---

## 🔮 Future Scope

1.  **Real-time Scoring**: Move from on-demand score calculation to event-driven updates (re-calculate score whenever a loan is paid).
2.  **Caching**: Cache credit scores in Redis with a TTL of 24h to reduce DB load on `/check-eligibility` endpoints.
3.  **Idempotency Keys**: Add header-based idempotency support for `/create-loan` to prevent double-spending on network retries.
4.  **Monitoring**: Add Prometheus/Grafana to track loan approval rates and ingestion latency.

---

## 🧪 API Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/register` | Register a new customer & calc approved limit |
| `POST` | `/check-eligibility` | Check loan approval chances & interest rate |
| `POST` | `/create-loan` | Sanction a new loan (Atomic Transaction) |
| `GET` | `/view-loan/{id}` | Get loan details |
| `GET` | `/view-loans/{cust_id}` | List all loans for a customer |

---
---

## 🛠️ Internal QA Interface

The project includes a lightweight, **zero-dependency** QA interface for internal testing and verification.

**Access**: `http://localhost:8000/qa/` (or via root redirect)

### How It Works
We serve static HTML templates via Django's `TemplateView` to avoid the complexity of a separate frontend app for internal tools.

1.  **Placement**: HTML files reside in `templates/qa/`.
2.  **Routing**: `apps.qa_interface.urls` maps these templates to URLs like `/qa/register/`.
3.  **Security**: These views are currently unprotected but can be easily wrapped with `login_required` or `user_passes_test(lambda u: u.is_staff)` for production safety.

### QA Checklist
Use the following checklist to verify the system reliability:

#### 1. Registration Flow
- [ ] **Register Valid User**: Ensure `approved_limit` is rounded to nearest lakh and calculated correctly based on salary.
- [ ] **Register Duplicate Phone**: Try registering the same phone number twice; should fail.

#### 2. Eligibility Flow
- [ ] **Good Credit**: Check eligibility for Customer 101 (Seeded). Should be APPROVED.
- [ ] **Bad Credit**: Check eligibility for Customer 102 (Seeded). Should be REJECTED or have higher interest.
- [ ] **High Debt**: Check Customer 103 (Seeded). Should fail if debt > limit.

#### 3. Loan Creation Flow
- [ ] **Create Loan**: Apply for a loan within the limit. Verify `loan_id` is returned.
- [ ] **Double Spending**: Click submit twice rapidly (if UI allows) or use Postman to send concurrent requests. (Future: Idempotency Key).

#### 4. Data Integrity
- [ ] **View Loan**: Verify interest rate and EMI match the values shown during eligibility check.
- [ ] **View Customer Loans**: Ensure the newly created loan appears in the customer's portfolio.

---

*Submitted by Sagar Dahiwal for Backend Assignment*
