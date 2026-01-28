from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "qa/index.html"

class RegisterView(TemplateView):
    template_name = "qa/register.html"

class EligibilityView(TemplateView):
    template_name = "qa/eligibility.html"

class ApplyView(TemplateView):
    template_name = "qa/apply.html"

class ViewLoanView(TemplateView):
    template_name = "qa/view_loan.html"

class CustomerLoansView(TemplateView):
    template_name = "qa/customer_loans.html"

