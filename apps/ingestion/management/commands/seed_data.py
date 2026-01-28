from django.core.management.base import BaseCommand
from django.conf import settings
from apps.ingestion.loaders import ExcelLoader
import os

class Command(BaseCommand):
    help = 'Seeds data from constant/ folder using ExcelLoader'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting data seeding from Excel files...")

        constant_dir = os.path.join(settings.BASE_DIR, 'constant')
        customer_file = os.path.join(constant_dir, 'customer_data.xlsx')
        loan_file = os.path.join(constant_dir, 'loan_data.xlsx')

        # 1. Load Customers
        if os.path.exists(customer_file):
            self.stdout.write(f"Loading customers from {customer_file}...")
            try:
                result = ExcelLoader.load_customers(customer_file)
                self.stdout.write(self.style.SUCCESS(f"Customers Loaded: {result}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to load customers: {e}"))
        else:
            self.stdout.write(self.style.WARNING(f"Customer file not found at {customer_file}"))

        # 2. Load Loans
        if os.path.exists(loan_file):
            self.stdout.write(f"Loading loans from {loan_file}...")
            try:
                result = ExcelLoader.load_loans(loan_file)
                self.stdout.write(self.style.SUCCESS(f"Loans Loaded: {result}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to load loans: {e}"))
        else:
            self.stdout.write(self.style.WARNING(f"Loan file not found at {loan_file}"))

        self.stdout.write(self.style.SUCCESS('Seeding Process Completed!'))
