from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from apps.customers.views import RegisterView
from apps.loans.views import (
    CheckEligibilityView, 
    CreateLoanView, 
    ViewLoanDetailView, 
    ViewLoansByCustomerView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # QA Interface
    path('qa/', include('apps.qa_interface.urls')),
    path('', RedirectView.as_view(url='/qa/', permanent=False)), # Redirect root to QA Dashboard

    
    # Customer Endpoints
    path('register', RegisterView.as_view(), name='register'),
    
    # Loan Endpoints
    path('check-eligibility', CheckEligibilityView.as_view(), name='check-eligibility'),
    path('create-loan', CreateLoanView.as_view(), name='create-loan'),
    path('view-loan/<int:loan_id>', ViewLoanDetailView.as_view(), name='view-loan-detail'),
    path('view-loans/<int:customer_id>', ViewLoansByCustomerView.as_view(), name='view-loans-by-customer'),
]
