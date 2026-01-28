from django.db import models
from apps.customers.models import Customer

class Loan(models.Model):
    # Implied status choices based on logic
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid'),
    ]

    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.PositiveIntegerField(help_text="Tenure in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Yearly interest rate")
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    emis_paid_on_time = models.PositiveIntegerField(default=0)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Loan {self.loan_id} - {self.customer}"
