from decimal import Decimal
import math

class InterestService:
    @staticmethod
    def calculate_monthly_installment(principal, rate, tenure_months):
        """
        Calculate monthly installment (EMI) using Standard Reducing Balance Matrix.
        Formula: E = P * r * (1+r)^n / ((1+r)^n - 1)
        
        Where:
        P = Principal
        r = Monthly Interest Rate (Annual Rate / 12 / 100)
        n = Tenure in Months
        """
        if tenure_months == 0:
            return Decimal(0)

        P = Decimal(principal)
        annual_rate = Decimal(rate)
        
        # Monthly Interest Rate (r)
        # 12% p.a -> 1% p.m -> 0.01
        r = annual_rate / Decimal(12) / Decimal(100)
        
        n = Decimal(tenure_months)
        
        if r == 0:
            return round(P / n, 2)
            
        # (1+r)^n
        pow_factor = Decimal(math.pow(1 + float(r), float(n)))
        
        # EMI = P * r * ((1+r)^n) / ((1+r)^n - 1)
        numerator = P * r * pow_factor
        denominator = pow_factor - 1
        
        emi = numerator / denominator
        
        return round(emi, 2)
