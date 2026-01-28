from rest_framework import serializers
from apps.customers.models import Customer
from apps.customers.services import CustomerService

class CustomerRegisterSerializer(serializers.ModelSerializer):
    monthly_income = serializers.IntegerField(source='monthly_salary')
    name = serializers.SerializerMethodField(read_only=True)
    customer_id = serializers.IntegerField(read_only=True)
    approved_limit = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'age', 'monthly_income', 'phone_number', 
            'customer_id', 'name', 'approved_limit'
        ]
        extra_kwargs = {
            'first_name': {'write_only': True},
            'last_name': {'write_only': True}
        }

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def create(self, validated_data):
        monthly_salary = validated_data.pop('monthly_salary')
        approved_limit = CustomerService.calculate_approved_limit(monthly_salary)
        
        customer = Customer.objects.create(
            monthly_salary=monthly_salary,
            approved_limit=approved_limit,
            **validated_data
        )
        return customer
