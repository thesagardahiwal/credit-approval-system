from decimal import Decimal
import math

class InterestService:
    @staticmethod
    def calculate_monthly_installment(principal, rate, tenure_months):
        """
        Calculate monthly installment (EMI) using compound interest formula.
        A = P * (1 + r/n)^(n*t)
        EMI = A / (months)
        
        Where:
        P = Principal Amount
        r = Annual Interest Rate (decimal)
        n = Number of times interest applied per time period (Assume monthly compounding? implied by compound interest requirement)
        
        Detailed requirement: "Use compound interest scheme for calculation of monthly interest."
        Usually EMI is calculated using: E = P * r * (1+r)^n / ((1+r)^n - 1)
        But requirement says: "Use compound interest scheme for calculation of monthly interest."
        
        Let's interpret strictly: 
        Total Amount Payble (A) with Compound Interest:
        A = P * (1 + R/100)^T
        Where T is time in years (tenure_months / 12)
        Then Monthly Installment = A / tenure_months
        """
        P = Decimal(principal)
        R = Decimal(rate)
        # Tenure in years
        T = Decimal(tenure_months) / Decimal(12)
        
        # Compound Interest Formula
        # A = P * (1 + R/100) ^ T
        # We need to handle Decimal powers carefully or convert to float for power
        
        rate_factor = (1 + R/100)
        # Using float for power calculation then converting back to Decimal
        total_amount = P * Decimal(math.pow(float(rate_factor), float(T)))
        
        monthly_installment = total_amount / Decimal(tenure_months)
        
        return round(monthly_installment, 2)
