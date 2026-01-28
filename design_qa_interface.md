# Internal QA Interface Design 🧪

## Overview
A lightweight, frontend-framework-free testing interface for the Credit Approval System. Designed for internal QA teams to validate API behavior visually without using Postman/Curl.

## 1. Pages Needed

We will create a specific HTML page for each key workflow.

| # | Page Name | File Name | Purpose |
| :--- | :--- | :--- | :--- |
| 1 | **QA Dashboard** | `index.html` | Central hub linking to all test tools. |
| 2 | **Customer Registration** | `register.html` | Test new user onboarding and credit limit logic. |
| 3 | **Loan Simulator** | `eligibility.html` | Test eligibility logic ("What if" scenarios). |
| 4 | **Loan Application** | `apply.html` | Test actual loan creation and transaction commitment. |
| 5 | **Customer 360** | `customer.html` | View customer profile and loan history (GET endpoints). |

## 2. Test Coverage Per Page

### A. Customer Registration (`register.html`)
- **Tests**: `POST /register`
- **Scenarios**:
    - Valid registration (Check if `approved_limit` is correctly calculated).
    - Invalid salary (Negative/Zero).
    - Duplicate phone number (Error handling).
    - Missing fields.

### B. Loan Simulator (`eligibility.html`)
- **Tests**: `POST /check-eligibility`
- **Features**: dynamic form to input Customer ID + Loan Details.
- **Scenarios**:
    - High Credit Score (>50) -> Approval.
    - Low Credit Score (<10) -> Rejection.
    - Interest Rate correction validation (Request 8%, get corrected to 12% or 16%).

### C. Loan Application (`apply.html`)
- **Tests**: `POST /create-loan`
- **Features**: Two-step flow (Check Eligibility result -> Apply).
- **Scenarios**:
    - Successful sanction.
    - Rejection due to Debt-to-Income ratio (Simulate by adding debts first).
    - Idempotency checks (if implemented).

### D. Customer 360 (`customer.html`)
- **Tests**: 
    - `GET /view-loans/{customer_id}`
    - Access `Customer` model via ID.
- **Features**: Read-only view of a customer's current state, debt, and loan list.

## 3. URL Routing Strategy

We will serve these pages as **Django Templates** using `TemplateView`. This avoids needing a separate web server or CORS configuration.

**App Name**: `apps.qa_interface` (New Django App)

**URL Configuration (`config/urls.py`)**:
```python
path('qa/', include('apps.qa_interface.urls'))
```

**App URLs (`apps/qa_interface/urls.py`)**:
```python
path('', IndexView.as_view(), name='qa-index'),
path('register/', RegisterView.as_view(), name='qa-register'),
path('eligibility/', EligibilityView.as_view(), name='qa-eligibility'),
path('apply/', ApplyView.as_view(), name='qa-apply'),
path('customer/', CustomerView.as_view(), name='qa-customer'),
```

## 4. File Structure

HTML files live in the Django Template directory pattern. Static assets (CSS/JS) live in `static/`.

```text
credit-approval-system/
├── apps/
│   └── qa_interface/
│       ├── urls.py
│       └── views.py        # Generic TemplateViews
├── templates/              # Global Templates Dir
│   └── qa/
│       ├── base.html       # Common layout (Nav, CSS includes)
│       ├── index.html
│       ├── register.html
│       ├── eligibility.html
│       └── apply.html
└── static/
    └── qa/
        ├── style.css       # Simple CSS (e.g. Bootstrap CDN or Vanilla)
        └── app.js          # Shared JS helpers (fetch wrapper, CSRF)
```

## 5. Technical Implementation Details

### CSRF Handling
Since we are using `fetch` from the same origin, we need to handle CSRF tokens.
- **HTML**: `{% csrf_token %}` injected into `base.html` (hidden).
- **JS**: A helper function `getCookie('csrftoken')` or reading the input value to include in `fetch` headers:
    ```javascript
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    }
    ```

### Vanilla JS Strategy
- Use `document.getElementById` for DOM access.
- Use `async/await` for API calls.
- **Output**: Display JSON responses in a `<pre>` tag for raw inspection, plus a simple parsed success/error banner.
