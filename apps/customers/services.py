class CustomerService:
    @staticmethod
    def calculate_approved_limit(monthly_salary):
        """
        approved_limit = 36 * monthly_salary (rounded to nearest lakh)
        """
        limit = 36 * monthly_salary
        # Round to nearest lakh (100,000)
        # Algorithm: round(number / 100000) * 100000
        approved_limit = round(limit / 100000) * 100000
        return approved_limit
