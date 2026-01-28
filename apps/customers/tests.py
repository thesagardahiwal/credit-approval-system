from django.test import TestCase
from apps.customers.models import Customer
from apps.customers.services import CustomerService

class CustomerServiceTest(TestCase):
    def test_approved_limit_calculation(self):
        # 36 * 10,000 = 360,000 -> round to nearest lakh -> 400,000?
        # 3.6 Lakhs. 
        # Round 3.6 to nearest integer is 4? 
        # Python rounding: 3.5 -> 4, 3.4 -> 3.
        # 360,000 / 100,000 = 3.6. 3.6 round -> 4. 4 * 100,000 = 400,000.
        
        salary = 10000
        limit = CustomerService.calculate_approved_limit(salary)
        self.assertEqual(limit, 400000)

        salary = 15000 # 36 * 15000 = 540,000 -> 5.4 -> 5 -> 500,000
        limit = CustomerService.calculate_approved_limit(salary)
        self.assertEqual(limit, 500000)

class CustomerAPITest(TestCase):
    def test_register_customer(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "monthly_income": 25000,
            "phone_number": "1234567890"
        }
        resp = self.client.post('/register', data)
        self.assertEqual(resp.status_code, 201)
        self.assertIn('customer_id', resp.data)
        self.assertEqual(resp.data['approved_limit'], 900000) # 25000 * 36 = 900,000 -> 9.0 -> 900,000
