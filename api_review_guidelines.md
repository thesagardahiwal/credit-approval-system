# API Review Guidelines: Loan Approval System

This document outlines common pitfalls candidates encounter when designing backend APIs for credit systems and how to mitigate them.

## 1. HTTP Status Codes & Semantics

### Common Mistakes
- **Everything is 200 OK**: Returning `200 OK` for failed validations with a body like `{"error": "Invalid tenure"}`. This breaks REST conventions and client error handling.
- **500 Internal Server Error for Validation**: Letting unhandled exceptions (e.g., `ValueError`) bubble up as 500s instead of catching them and returning `400 Bad Request`.
- **201 vs 200**: Returning `200 OK` after successfully creating a resource (Loan/Customer) instead of `201 Created`.

### Best Practices
- **201 Created**: For `/register` and `/create-loan` on success.
- **400 Bad Request**: For malformed data (negative salary, missing fields) or domain rule violations (tenure too short).
- **404 Not Found**: If `customer_id` does not exist.
- **422 Unprocessable Entity**: (Optional) For semantically incorrect data (valid JSON, but invalid logic).

## 2. Input Validation & Data Types

### Common Mistakes
- **Floats for Money**: Using `Float` fields for currency.
    - *Risk*: `0.1 + 0.2 != 0.3`. Floating point math leads to penny-shaving errors.
    - *Fix*: Always use `Decimal` with fixed precision (e.g., 2 decimal places).
- **Trusting the Client**: Accepting `approved_limit` from the request body in `/register`.
    - *Fix*: The backend must calculate sensitive fields based on validated inputs (`monthly_salary`).
- **Missing Range Checks**: Allowing `age: -5` or `tenure: 0`.
    - *Risk*: `DivisionByZero` errors in logic or nonsensical data.
- **Date Parsing**: Naive string-to-date conversion without checking format, leading to crashes.

## 3. Transactions & Concurrency (Critical)

### Common Mistakes
- **No Atomicity**: Logic that acts on multiple tables without `transaction.atomic()`.
    - *Scenario*: `/create-loan` creates a `Loan` entry but fails to calculate EMI or update `current_debt`. The DB is left in an inconsistent state.
- **Race Conditions (Double Spending)**:
    - *Scenario*: User has limit ₹10k, owes ₹0. Two requests for ₹10k loan come in simultaneously.
    - *Bug*: Request A reads debt=0. Request B reads debt=0. Both check `0 + 10k <= 10k` (True). Both output "Approved". User gets ₹20k loans.
    - *Fix*: Use `select_for_update()` to lock the Customer row during eligibility checks.

## 4. Edge Cases

### Common Mistakes
- **Zero Division**: Calculating repayment components when `tenure=0` or `interest=0` (if logic uses division).
- **Credit Score Boundaries**:
    - *Bug*: "If score > 50" (Approves 51+) and "If score < 50" (Approves 49-). **Score 50 is orphaned** and handled by neither or fallback.
    - *Fix*: Use explicit inclusive bounds (`>=`).
- **Pagination**: Returning `Loan.objects.all()` in `/view-loans`.
    - *Risk*: System crashes when a customer has 10,000 loans.
    - *Fix*: Implement pagination (limit/offset).

## 5. Security & Performance

### Common Mistakes
- **N+1 Queries**: In `/view-loans`, iterating through loans and fetching `loan.customer.first_name` inside the loop.
    - *Fix*: Use `select_related('customer')` in the queryset.
- **Information Leakage**: Returning full stack traces in production API responses.

---

## Example: Proper Transactional Loan Creation

```python
from django.db import transaction

def create_loan(customer_id, amount):
    with transaction.atomic():
        # Lock customer row to prevent race conditions
        customer = Customer.objects.select_for_update().get(pk=customer_id)
        
        # Check eligibility with locked data
        if customer.current_debt + amount > customer.approved_limit:
            return {"error": "Limit exceeded"}
            
        # Create loan
        Loan.objects.create(...)
        
        # Update debt state if denormalized
        customer.current_debt += amount
        customer.save()
```
