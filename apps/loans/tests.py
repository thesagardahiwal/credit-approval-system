from django.test import TestCase
from apps.customers.models import Customer
from apps.loans.models import Loan
from apps.loans.services.loan_service import LoanService

class LoanServiceTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Jane",
            last_name="Doe",
            phone_number="9876543210",
            monthly_salary=50000,
            approved_limit=1800000, # 50k * 36 = 1.8M
            age=25
        )

    def test_loan_logic_new_customer(self):
        # New customer has 0 loans, 0 credit score?
        # Logic: 
        # Past loans paid on time: 0
        # Loans taken: 0
        # Activity current year: 0
        # Approved volume: 0
        # Score = 0
        # Score <= 10 -> Don't approve.
        
        result = LoanService.check_eligibility(
            self.customer.customer_id,
            loan_amount=50000,
            interest_rate=10,
            tenure=12
        )
        self.assertFalse(result['approval'])
    
    def test_loan_logic_good_score_simulation(self):
        # Hack to simulate credit score logic dependency or mock it?
        # Since we use database queries, we can seed data.
        
        # Create a paid past loan to boost score
        Loan.objects.create(
            customer=self.customer,
            loan_amount=50000,
            tenure=12,
            interest_rate=10,
            status='PAID',
            emis_paid_on_time=12,
            end_date="2023-01-01"
        )
        # Score += 20 (Paid loan)
        # Score += 10 (Total loans > 0)
        # Score = 30.
        
        # 30 >= Score > 10: Approve with interest > 16%.
        
        result = LoanService.check_eligibility(
            self.customer.customer_id,
            loan_amount=10000,
            interest_rate=10, # Requesting 10%
            tenure=12
        )
        
        # Should be approved but with corrected interest rate 16%?
        # Requirement: "If 30> credit_rating > 10 , approve loans with interest rate >16%"
        # Wait, if score is exactly 30: "50 > credit_rating > 30" (31-49), "30> credit_rating > 10" (11-29).
        # My code:
        # if credit_score > 50: ...
        # elif 50 >= credit_score > 30: ...
        # elif 30 >= credit_score > 10: ... (This catches 30)
        
        self.assertTrue(result['approval'])
        self.assertEqual(result['corrected_interest_rate'], 16)
