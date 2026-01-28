from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.customers.serializers import CustomerRegisterSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
