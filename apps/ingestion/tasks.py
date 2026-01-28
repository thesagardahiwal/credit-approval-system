import pandas as pd
from celery import shared_task
from apps.customers.models import Customer
from apps.loans.models import Loan
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@shared_task
def ingest_customer_data(file_path):
    try:
        df = pd.read_excel(file_path)
        # expected columns: customer_id, first_name, last_name, phone_number, monthly_salary, approved_limit, current_debt
        
        customers = []
        for _, row in df.iterrows():
            try:
                # Basic validation or cleaning could go here
                customers.append(Customer(
                    customer_id=row['Customer ID'], # Adjust column name based on actual excel
                    first_name=row['First Name'],
                    last_name=row['Last Name'],
                    phone_number=str(row['Phone Number']),
                    monthly_salary=row['Monthly Salary'],
                    approved_limit=row['Approved Limit'],
                    current_debt=row.get('Current Debt', 0), # Optional handling
                    age=row['Age']
                ))
            except Exception as e:
                logger.error(f"Error processing customer row {row}: {e}")
        
        # Bulk create for efficiency, ignoring conflicts if possible or handling them
        Customer.objects.bulk_create(customers, ignore_conflicts=True)
        logger.info(f"Successfully ingested {len(customers)} customers.")
    except Exception as e:
        logger.error(f"Failed to ingest customer data: {e}")

@shared_task
def ingest_loan_data(file_path):
    try:
        df = pd.read_excel(file_path)
        # expected columns: customer id, loan id, loan amount, tenure, interest rate, monthly repayment, EMIs paid on time, start date, end date
        
        loans = []
        for _, row in df.iterrows():
            try:
                # We need to find the customer instance. 
                # Ideally bulk ingestion implies we trust the IDs or they exist.
                # Only adding if customer exists
                customer_id = row['Customer ID']
                if not Customer.objects.filter(customer_id=customer_id).exists():
                    logger.warning(f"Customer {customer_id} not found for loan {row['Loan ID']}")
                    continue

                loans.append(Loan(
                    loan_id=row['Loan ID'],
                    customer_id=customer_id,
                    loan_amount=row['Loan Amount'],
                    tenure=row['Tenure'],
                    interest_rate=row['Interest Rate'],
                    monthly_repayment=row['Monthly payment'],
                    emis_paid_on_time=row['EMIs paid on Time'],
                    start_date=pd.to_datetime(row['Date of Approval']).date(),
                    end_date=pd.to_datetime(row['End Date']).date(),
                    status='APPROVED' # Historical data assumed approved
                ))
            except Exception as e:
                logger.error(f"Error processing loan row {row}: {e}")

        Loan.objects.bulk_create(loans, ignore_conflicts=True)
        logger.info(f"Successfully ingested {len(loans)} loans.")
    except Exception as e:
        logger.error(f"Failed to ingest loan data: {e}")
