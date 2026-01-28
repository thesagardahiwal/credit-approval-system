# Credit Score Algorithm Design

## Overview
The credit score is a numerical expression (0–100) representing the creditworthiness of a customer. This algorithm focuses on transparency, using four key components derived from the user's loan history.

## Components & Weights

The total score (100) is divided into four weighted categories:

1.  **Past Repayment Behavior (Weight: 35%)**
    *   **Rationale**: The strongest predictor of future performance is past behavior.
    *   **Metric**: Weighted ratio of EMIs paid on time vs. total EMIs due across all past loans.
    *   **Formula**:
        $$ Score_{repayment} = \left( \frac{\sum \text{EMIs Paid On Time}}{\sum \text{Total EMIs Due (Past/Closed Loans)}} \right) \times 35 $$
    *   **Normalization**: If no past loans exist, this component defaults to 0.

2.  **Loan Approved Volume (Weight: 25%)**
    *   **Rationale**: Demonstrates the customer's experience handling debt. Higher volume successfully managed implies higher trust.
    *   **Metric**: Total principal amount of all *approved* and *closed* loans.
    *   **Formula**:
        $$ Score_{volume} = \min \left( \frac{\text{Total Approved Volume}}{\text{Benchmark Volume}}, 1.0 \right) \times 25 $$
    *   **Normalization**: Benchmark Volume is set to ₹10,00,000 (10 Lakhs). Any volume above this gets full points.

3.  **Number of Loans (Weight: 20%)**
    *   **Rationale**: A higher number of loans indicates a thicker credit file and credit hungriness/experience.
    *   **Metric**: Count of distinct loans taken in the past.
    *   **Formula**:
        $$ Score_{count} = \min \left( \frac{\text{Total Loan Count}}{10}, 1.0 \right) \times 20 $$
    *   **Normalization**: Capped at 10 loans. 10 or more loans yield max points.

4.  **Current Year Activity (Weight: 20%)**
    *   **Rationale**: Recent activity indicates current financial stability and active credit participation.
    *   **Metric**: Number of loans active or opened in the current year.
    *   **Formula**:
        $$ Score_{activity} = \min \left( \frac{\text{Loans This Year}}{3}, 1.0 \right) \times 20 $$
    *   **Normalization**: Capped at 3 loans. We reward moderate activity.

## Edge Cases & Hard Rules

Regardless of the calculated score, the following overriding rules apply:

1.  **Debt Overload (Score = 0)**:
    *   Condition: `Sum(Current Consumer Debt) > Approved Credit Limit`
    *   Result: Credit Score is forced to **0**.

2.  **No History (Score = 0)**:
    *   Condition: Customer has 0 previous loans.
    *   Result: Score is 0.

## Implementation Details

The algorithm is implemented in `apps.loans.services.credit_score.CreditScoreService`.
