from decimal import Decimal
from apps.customers.models import Customer
from apps.loans.models import Loan
from apps.loans.services.credit_score import CreditScoreService
from apps.loans.services.interest import InterestService
from django.db.models import Sum
from datetime import date

class LoanService:
    @staticmethod
    def check_eligibility(customer_id, loan_amount, interest_rate, tenure):
        customer = Customer.objects.get(customer_id=customer_id)
        credit_score = CreditScoreService.calculate_credit_score(customer_id)
        
        approved = False
        corrected_interest_rate = interest_rate
        
        # Credit Score Rules
        if credit_score > 50:
            approved = True
        elif 50 >= credit_score > 30:
            if interest_rate < 12:
                corrected_interest_rate = 12
            approved = True
        elif 30 >= credit_score > 10:
            if interest_rate < 16:
                corrected_interest_rate = 16
            approved = True
        else: # credit_score <= 10
            approved = False
            
        # Check Total EMI constraint
        # "If sum of all current EMIs > 50% of monthly salary, don’t approve any loans"
        # We need to calculate the NEW EMI as well to see if it pushes over the limit?
        # Requirement says "sum of all current EMIs". Does this include the requested one?
        # Usually checking eligibility implies checking if the NEW loan is affordable.
        # Let's assume strict reading: "sum of all CURRENT emis" implies existing ones.
        # But if we add a new one, we should probably check if (Existing + New) > 50% Salary.
        # Let's be safe and check Total + New.
        
        current_emis = Loan.objects.filter(
            customer=customer, 
            status__in=['APPROVED', 'PENDING'],
            end_date__gte=date.today() # Only active loans? Logic implied by "current"
        ).aggregate(Sum('monthly_repayment'))['monthly_repayment__sum'] or 0
        
        new_emi = InterestService.calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
        
        if (current_emis + new_emi) > (0.5 * customer.monthly_salary):
            approved = False
            
        return {
            'customer_id': customer_id,
            'approval': approved,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': tenure,
            'monthly_installment': new_emi
        }

    @staticmethod
    def create_loan(customer_id, loan_amount, interest_rate, tenure):
        eligibility = LoanService.check_eligibility(customer_id, loan_amount, interest_rate, tenure)
        
        if eligibility['approval']:
            # Create loan
            loan = Loan.objects.create(
                customer_id=customer_id,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=eligibility['corrected_interest_rate'],
                monthly_repayment=eligibility['monthly_installment'],
                status='APPROVED'
            )
            return {
                'loan_id': loan.loan_id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': 'Loan approved successfully',
                'monthly_installment': eligibility['monthly_installment']
            }
        else:
            return {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': 'Loan not approved based on eligibility criteria',
                'monthly_installment': 0
            }
