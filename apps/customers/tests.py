from django.test import TestCase
from django.urls import reverse
from apps.customers.models import Customer
from apps.customers.services.customer_service import CustomerService

class CustomerServiceTests(TestCase):
    """
    Validates rules for onboarding customers.
    """
    def test_approved_limit_rounding(self):
        """
        Limit should be 36 * monthly_salary, rounded to nearest lakh (100,000).
        """
        # Case A: 10,000 * 36 = 360,000 -> 3.6L -> Rounds to 4L (400,000)
        limit_a = CustomerService.calculate_approved_limit(10000)
        self.assertEqual(limit_a, 400000)

        # Case B: 15,000 * 36 = 540,000 -> 5.4L -> Rounds to 5L (500,000)
        limit_b = CustomerService.calculate_approved_limit(15000)
        self.assertEqual(limit_b, 500000)

        # Case C: 27,000 * 36 = 972,000 -> 9.72L -> Rounds to 10L (1,000,000)
        limit_c = CustomerService.calculate_approved_limit(27000)
        self.assertEqual(limit_c, 1000000)

class CustomerAPITests(TestCase):
    """
    Validates Customer API endpoints.
    """
    def test_register_customer_endpoint(self):
        payload = {
            "first_name": "Alice",
            "last_name": "Wonder",
            "age": 25,
            "monthly_income": 45000,
            "phone_number": "9876598765"
        }
        
        response = self.client.post(reverse('register'), payload, content_type='application/json')
        
        # Assertions
        self.assertEqual(response.status_code, 201, "Should return 201 Created")
        data = response.json()
        
        self.assertIn('customer_id', data)
        self.assertIn('approved_limit', data)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "Alice Wonder")
        
        # Verify DB creation
        self.assertTrue(Customer.objects.filter(phone_number="9876598765").exists())

    def test_duplicate_registration_fails(self):
        # 1. Create user
        Customer.objects.create(
            first_name="Bob", last_name="Builder",
            phone_number="1112223333", monthly_salary=30000,
            approved_limit=1000000, age=40
        )
        
        # 2. Try to register same phone
        payload = {
            "first_name": "Bob", "last_name": "Clone",
            "age": 22, "monthly_income": 20000,
            "phone_number": "1112223333"
        }
        
        # Expecting failure handled by Serializer (400 Bad Request)
        response = self.client.post(reverse('register'), payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)
