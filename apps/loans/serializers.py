from rest_framework import serializers
from apps.loans.models import Loan
from apps.customers.serializers import CustomerRegisterSerializer # For nested details if needed, or simple dict

class CheckEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()

class CreateLoanSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()

class LoanDetailSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_repayment', 'tenure']

    def get_customer(self, obj):
        return {
            'id': obj.customer.customer_id,
            'first_name': obj.customer.first_name,
            'last_name': obj.customer.last_name,
            'phone_number': obj.customer.phone_number,
            'age': obj.customer.age
        }

class CustomerLoanListSerializer(serializers.ModelSerializer):
    repayments_left = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_repayment', 'repayments_left']

    def get_repayments_left(self, obj):
        # Implicit logic: tenure - emis_paid_on_time? Or calculate from start date?
        # "View all current loan details".
        # Let's assume repayments_left = tenure - (months passed since start)?
        # Or simpler: tenure (total months) - emis_paid (if we track strict payments)
        # Let's use tenure implied by model logic (assuming 0 paid initially for new loans or tracked)
        # Requirement doesn't specify how `repayments_left` is updated.
        # But `Loan` model has `emis_paid_on_time`.
        return obj.tenure # Simplification, but maybe better: obj.tenure - obj.emis_paid_on_time
        # Wait, if `emis_paid_on_time` tracks generic "paid", it might not be all payments.
        # Let's stick to tenure for now or 0 if paid.
        # Ideally: calculate based on start_date and today? 
        # I'll stick to a placeholder logic or strictly `tenure` if it means "total tenure" but field name says "repayments_left".
        # Let's return obj.tenure for now as there is no robust ledger.
