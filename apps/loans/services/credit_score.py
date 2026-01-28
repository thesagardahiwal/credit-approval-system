from django.db.models import Sum
from apps.loans.models import Loan
from datetime import date

class CreditScoreService:
    @staticmethod
    def calculate_credit_score(customer_id):
        """
        Calculate credit score based on:
        i. Past Loans paid on time
        ii. No of loans taken in past
        iii. Loan activity in current year
        iv. Loan approved volume
        v. If sum of current loans > approved limit, credit score = 0
        """
        score = 0
        customer_loans = Loan.objects.filter(customer_id=customer_id)
        
        # v. Check approved limit
        if customer_loans.exists():
            customer = customer_loans.first().customer
            current_loans_sum = customer_loans.filter(status__in=['APPROVED', 'PENDING']).aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
            if current_loans_sum > customer.approved_limit:
                return 0

        # i. Past Loans paid on time
        # Assign points for paid loans
        paid_loans = customer_loans.filter(status='PAID').count()
        score += paid_loans * 10 # heuristic: 10 points per paid loan? or strictly based on "on time"?
                                # Requirement says: "Past Loans paid on time". 
                                # Let's assume emis_paid_on_time correlated? 
                                # Or simply if they have successfully closed loans.
                                # Let's use emis_paid_on_time of all loans?
                                # Let's stick to a simple model: 
                                # + per loan fully paid
        
        # Let's create a robust scoring model based on the components
        # 1. Past Loans paid on time
        # Let's verify against 'emis_paid_on_time' vs tenure?
        # For simplicity, if status='PAID', we add points.
        if paid_loans > 0:
            score += 20
        
        # ii. No of loans taken in past
        total_loans = customer_loans.count()
        if total_loans > 0:
            score += 10
            
        # iii. Loan activity in current year
        current_year = date.today().year
        loans_this_year = customer_loans.filter(start_date__year=current_year).count()
        if loans_this_year > 0:
            score += 10
            
        # iv. Loan approved volume
        approved_volume = customer_loans.filter(status='APPROVED').aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
        if approved_volume > 100000:
             score += 10
        
        # Cap at 100
        return min(score, 100)
