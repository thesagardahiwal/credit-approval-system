import pandas as pd
from apps.customers.models import Customer
from apps.loans.models import Loan
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ExcelLoader:
    BATCH_SIZE = 1000

    @staticmethod
    def load_customers(file_path):
        try:
            df = pd.read_excel(file_path)
            total_rows = len(df)
            success_count = 0
            fail_count = 0
            errors = []
            
            batch = []
            
            for index, row in df.iterrows():
                try:
                    phone = str(row['Phone Number'])
                    if not phone:
                        raise ValueError("Missing Phone Number")
                        
                    customer = Customer(
                        customer_id=row['Customer ID'],
                        first_name=row['First Name'],
                        last_name=row['Last Name'],
                        phone_number=phone,
                        monthly_salary=row['Monthly Salary'],
                        approved_limit=row['Approved Limit'],
                        current_debt=row.get('Current Debt', 0),
                        age=row['Age']
                    )
                    batch.append(customer)
                    
                    if len(batch) >= ExcelLoader.BATCH_SIZE:
                        Customer.objects.bulk_create(batch, ignore_conflicts=True)
                        success_count += len(batch)
                        batch = []
                        
                except Exception as e:
                    fail_count += 1
                    errors.append(f"Row {index}: {str(e)}")
            
            if batch:
                Customer.objects.bulk_create(batch, ignore_conflicts=True)
                success_count += len(batch)
                
            return {
                'total': total_rows,
                'success': success_count,
                'failed': fail_count,
                'errors': errors
            }
        except Exception as e:
            logger.error(f"Fatal error loading customers: {e}")
            raise e

    @staticmethod
    def load_loans(file_path):
        try:
            df = pd.read_excel(file_path)
            total_rows = len(df)
            success_count = 0
            fail_count = 0
            errors = []
            
            batch = []
            existing_customer_ids = set(Customer.objects.values_list('customer_id', flat=True))
            
            for index, row in df.iterrows():
                try:
                    customer_id = row['Customer ID']
                    if customer_id not in existing_customer_ids:
                        raise ValueError(f"Customer {customer_id} does not exist")

                    loan = Loan(
                        loan_id=row['Loan ID'],
                        customer_id=customer_id,
                        loan_amount=row['Loan Amount'],
                        tenure=row['Tenure'],
                        interest_rate=row['Interest Rate'],
                        monthly_repayment=row['Monthly payment'],
                        emis_paid_on_time=row['EMIs paid on Time'],
                        start_date=pd.to_datetime(row['Date of Approval']).date(),
                        end_date=pd.to_datetime(row['End Date']).date(),
                        status='APPROVED' 
                    )
                    batch.append(loan)
                    
                    if len(batch) >= ExcelLoader.BATCH_SIZE:
                        Loan.objects.bulk_create(batch, ignore_conflicts=True)
                        success_count += len(batch)
                        batch = []

                except Exception as e:
                    fail_count += 1
                    errors.append(f"Row {index}: {str(e)}")

            if batch:
                Loan.objects.bulk_create(batch, ignore_conflicts=True)
                success_count += len(batch)

            return {
                'total': total_rows,
                'success': success_count,
                'failed': fail_count,
                'errors': errors
            }
        except Exception as e:
            logger.error(f"Fatal error loading loans: {e}")
            raise e
