from django.db.models import Sum
from apps.loans.models import Loan
from datetime import date
import redis
import os

# Redis connection
redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    db=int(os.environ.get('REDIS_DB', 1)),
    decode_responses=True
)

class CreditScoreService:
    CACHE_TTL = 86400  # 24 hours in seconds
    CACHE_KEY_PREFIX = 'credit_score:'
    
    @staticmethod
    def get_cache_key(customer_id):
        """Generate cache key for customer credit score."""
        return f"{CreditScoreService.CACHE_KEY_PREFIX}{customer_id}"
    
    @staticmethod
    def invalidate_cache(customer_id):
        """Invalidate credit score cache for a customer (called after new loan creation)."""
        cache_key = CreditScoreService.get_cache_key(customer_id)
        try:
            redis_client.delete(cache_key)
        except Exception as e:
            # If Redis is unavailable, silently continue
            pass
    
    @staticmethod
    def calculate_credit_score(customer_id):
        """
        Calculate credit score based on:
        i. Past Loans paid on time
        ii. No of loans taken in past
        iii. Loan activity in current year
        iv. Loan approved volume
        v. If sum of current loans > approved limit, credit score = 0
        
        Result is cached for 24 hours to reduce database load.
        """
        # Check cache first
        cache_key = CreditScoreService.get_cache_key(customer_id)
        try:
            cached_score = redis_client.get(cache_key)
            if cached_score is not None:
                return int(cached_score)
        except Exception as e:
            # If Redis is unavailable, continue with calculation
            pass
        
        score = 0
        customer_loans = Loan.objects.filter(customer_id=customer_id)
        
        # v. Check approved limit - Edge Case: Score 0 if debt > limit
        if customer_loans.exists():
            customer = customer_loans.first().customer
            current_loans_sum = customer_loans.filter(status__in=['APPROVED', 'PENDING']).aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
            if current_loans_sum > customer.approved_limit:
                return 0

        # Component 1: Past Repayment Behavior (Weight: 35%)
        # Score = (Total EMIs Paid on Time / Total EMIs Expected) * 35
        # We need total tenure vs total paid across completed/active loans
        total_emis_paid = customer_loans.aggregate(Sum('emis_paid_on_time'))['emis_paid_on_time__sum'] or 0
        total_tenure = customer_loans.aggregate(Sum('tenure'))['tenure__sum'] or 0
        
        if total_tenure > 0:
            repayment_ratio = total_emis_paid / total_tenure
            # Cap ratio at 1.0 just in case data is weird
            repayment_ratio = min(repayment_ratio, 1.0)
            score += repayment_ratio * 35
        
        # Component 2: Number of Loans (Weight: 20%)
        # Score = (Count / 10) * 20, max 20
        total_loans_count = customer_loans.count()
        if total_loans_count > 0:
            count_factor = min(total_loans_count / 10, 1.0)
            score += count_factor * 20
            
        # Component 3: Current Year Activity (Weight: 20%)
        # Score = (Loans this year / 3) * 20, max 20
        current_year = date.today().year
        loans_this_year = customer_loans.filter(start_date__year=current_year).count()
        if loans_this_year > 0:
            activity_factor = min(loans_this_year / 3, 1.0)
            score += activity_factor * 20
            
        # Component 4: Loan Approved Volume (Weight: 25%)
        # Score = (Volume / 10,00,000) * 25, max 25
        approved_volume = customer_loans.filter(status__in=['APPROVED', 'PAID']).aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
        if approved_volume > 0:
            volume_factor = min(float(approved_volume) / 1000000, 1.0)
            score += volume_factor * 25
        
        final_score = round(min(score, 100))
        
        # Cache the score for 24 hours
        try:
            redis_client.setex(cache_key, CreditScoreService.CACHE_TTL, final_score)
        except Exception as e:
            # If Redis is unavailable, continue without caching
            pass
        
        return final_score
