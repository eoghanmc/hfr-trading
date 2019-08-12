from django.shortcuts import render
from django.views import generic
from trading.models import Fund, Portfolio
from .forms import UploadFileForm, GenerateTradesForm, UploadDailyPositionForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


# Create index/homepage view (functions-based)
@login_required(login_url='login')
def index(request):

    # Generate count of all funds
    num_funds = Fund.objects.all().count()

    # Generate count of all 'Active' num_funds
    num_active_funds = Fund.objects.filter(status__exact='Active').count()

    # Generate count of all unique Index ISINs
    num_index_isin_unique = Fund.objects.all().values('index_isin')\
        .distinct().count()

    # Generate context (aka output data)
    context = {
        "num_funds": num_funds,
        "num_active_funds": num_active_funds,
        "num_unique_index_funds": num_index_isin_unique,
    }

    # Render request with context data
    return render(request, 'index.html', context)


# Create Fund List page (class-based)
class FundView(LoginRequiredMixin, generic.ListView):
    model = Fund
    login_url = 'login'
    redirect_field_name = 'redirect_to'

# Create Portfolio List page (class-based)


class PortfoliosView(LoginRequiredMixin, generic.ListView):
    model = Portfolio
    login_url = 'login'
    redirect_field_name = 'redirect_to'


# Create Fund Detail page (class-based)
class FundDetailView(LoginRequiredMixin, generic.DetailView):
    model = Fund
    login_url = 'login'
    redirect_field_name = 'redirect_to'


class FundUploaderView(LoginRequiredMixin, generic.FormView):
    template_name = 'upload-file.html'
    form_class = UploadFileForm
    success_url = reverse_lazy('funds')
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        form.processs_data()
        return super().form_valid(form)


class PositionUploaderView(LoginRequiredMixin, generic.FormView):
    template_name = 'upload-positions.html'
    form_class = UploadDailyPositionForm
    success_url = reverse_lazy('')
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        form.processs_data()
        return super().form_valid(form)


class GenerateTradesView(LoginRequiredMixin, generic.FormView):
    template_name = 'generate-trades-form.html'
    form_class = GenerateTradesForm
