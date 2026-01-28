from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from apps.loans.serializers import CheckEligibilitySerializer, CreateLoanSerializer, LoanDetailSerializer, CustomerLoanListSerializer
from apps.loans.services.loan_service import LoanService
from apps.loans.models import Loan

class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            result = LoanService.check_eligibility(
                customer_id=data['customer_id'],
                loan_amount=data['loan_amount'],
                interest_rate=data['interest_rate'],
                tenure=data['tenure']
            )
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateLoanView(APIView):
    def post(self, request):
        serializer = CreateLoanSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            result = LoanService.create_loan(
                customer_id=data['customer_id'],
                loan_amount=data['loan_amount'],
                interest_rate=data['interest_rate'],
                tenure=data['tenure']
            )
            # requirement says response body needs 'loan_id', etc.
            # result structure matches requirement.
            return Response(result, status=status.HTTP_201_CREATED if result['loan_approved'] else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ViewLoanDetailView(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanDetailSerializer
    lookup_field = 'loan_id'

class ViewLoansByCustomerView(generics.ListAPIView):
    serializer_class = CustomerLoanListSerializer

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return Loan.objects.filter(customer_id=customer_id)
