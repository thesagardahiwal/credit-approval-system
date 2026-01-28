from celery import shared_task
from apps.ingestion.loaders import ExcelLoader
import logging

logger = logging.getLogger(__name__)

@shared_task
def ingest_customer_data(file_path):
    """
    Ingest customer data using ExcelLoader.
    """
    try:
        result = ExcelLoader.load_customers(file_path)
        summary = f"Customer Ingestion Complete. {result}"
        logger.info(summary)
        return summary
    except Exception as e:
        logger.error(f"Fatal error in customer ingestion: {e}")
        return f"Failed: {e}"

@shared_task
def ingest_loan_data(file_path):
    """
    Ingest loan data using ExcelLoader.
    """
    try:
        result = ExcelLoader.load_loans(file_path)
        summary = f"Loan Ingestion Complete. {result}"
        logger.info(summary)
        return summary
    except Exception as e:
        logger.error(f"Fatal error in loan ingestion: {e}")
        return f"Failed: {e}"
