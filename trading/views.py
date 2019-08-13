from django.shortcuts import render
from django.views import generic
from trading.models import Fund, Portfolio, Position, Calendar
from .forms import UploadFileForm, GenerateTradesForm, UploadDailyPositionForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import plotly.offline as opy
import plotly.graph_objs as go


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

    # graph example
    portfolios = Portfolio.objects.all()
    labels = [x['name'] for x in portfolios.values()]
    values = [x.get_position_sum() for x in portfolios]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    div = opy.plot(fig, auto_open=False, output_type='div', config={
        'displayModeBar': False})

    # Generate context (aka output data)
    context = {
        "num_funds": num_funds,
        "num_active_funds": num_active_funds,
        "num_unique_index_funds": num_index_isin_unique,
        "graph": div
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

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add in a QuerySet of all the portfolio sum
        context['portfolios_sum'] = "%.2f" % list(
            Position.objects.aggregate(Sum('value')).values())[0]
        return context


class CalendarView(LoginRequiredMixin, generic.ListView):
    """
    Create Calendar list page
    """
    model = Calendar
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
    success_url = reverse_lazy('index')
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        form.processs_data()
        return super().form_valid(form)


class GenerateTradesView(LoginRequiredMixin, generic.FormView):
    template_name = 'generate-trades-form.html'
    form_class = GenerateTradesForm
    success_url = reverse_lazy('index')
    login_url = 'login'
    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        form.process_data()
        return super().form_valid(form)
