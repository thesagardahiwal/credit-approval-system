from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, unique=True)
    monthly_salary = models.PositiveIntegerField()
    approved_limit = models.PositiveIntegerField(default=0)
    current_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    age = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
