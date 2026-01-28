from django.urls import path
from .views import (
    IndexView, RegisterView, EligibilityView, 
    ApplyView, ViewLoanView, CustomerLoansView
)

urlpatterns = [
    path('', IndexView.as_view(), name='qa-index'),
    path('register/', RegisterView.as_view(), name='qa-register'),
    path('eligibility/', EligibilityView.as_view(), name='qa-eligibility'),
    path('apply/', ApplyView.as_view(), name='qa-apply'),
    path('view-loan/', ViewLoanView.as_view(), name='qa-view-loan'),
    path('customer-loans/', CustomerLoansView.as_view(), name='qa-customer-loans'),
]
