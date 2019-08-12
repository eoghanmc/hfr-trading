import io
import csv
from django import forms
from .models import Fund, Portfolio, Position


class GenerateTradesForm(forms.Form):

    # Fields (inputs)
    account = forms.ModelChoiceField(queryset=None)
    trade_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    net_flows = forms.FloatField()
    trade_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(
            ('Cash', 'Cash'), ('Rebalance', 'Rebalance'), ('Both', 'Both'))
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Portfolio.objects.all()


class UploadFileForm(forms.Form):
    # Fields / input
    file = forms.FileField()

    # Methods
    def clean_data_file(self):
        f = self.cleaned_data['file']
        if f:
            ext = f.name.split('.')[-1]
            if ext != 'csv':
                raise forms.ValidationError('File type not supported')
        return f

    def processs_data(self):
        f = io.TextIOWrapper(self.clean_data_file().file)
        reader = csv.DictReader(f)

        for fund in reader:
            new_fund = dict(fund)
            Fund.objects.create(
                status='Active',
                isin=new_fund['isin'],
                index_isin=new_fund['index_isin'],
                name=new_fund['name'],
                firm=new_fund['firm'],
                style=new_fund['style'],
                strategy=new_fund['strategy'],
                flag_restrcited=new_fund['flag_restricted'],
                flag_late_cutoff=new_fund['flag_late_cutoff'],
                flag_units_trading=new_fund["flag_units_trading"],
                terms_rank=new_fund["terms_rank"],
                terms_rank_amount=new_fund["terms_rank_amount"],
                terms_sub_notice=new_fund["terms_sub_notice"],
                terms_sub_settlement=new_fund["terms_sub_settlement"],
                terms_sub_minimum=new_fund["terms_sub_minimum"],
                terms_red_notice=new_fund["terms_red_notice"],
                terms_red_settlement=new_fund["terms_red_settlement"],
                terms_cutoff_time=new_fund["terms_cutoff_time"],
                terms_calendars=new_fund["terms_calendars"],
                terms_man_fee=new_fund["terms_man_fee"],
                terms_perf_fee=new_fund["terms_perf_fee"]
            )


class UploadDailyPositionForm(forms.Form):

    # Fields
    file = forms.FileField()

    # Methods
    def clean_data_file(self):
        f = self.cleaned_data['file']
        if f:
            ext = f.name.split('.')[-1]
            if ext != 'csv':
                raise forms.ValidationError('File type not supported')
        return f

    def processs_data(self):
        f = io.TextIOWrapper(self.clean_data_file().file)
        reader = csv.DictReader(f)

        for line_position in reader:
            new_position = dict(line_position)

            # Get corresponding Fund (by ISIN) object
            fund_link = Fund.objects.get(pk=new_position['ISIN Number'])

            # Get corresponding Portfolio (by Acount Number) object
            portfolio_link = Portfolio.objects.get(pk=new_position['Fund'])

            # check if position line item is cash
            if new_position['Fund Asset Class'] == 'CURRENCY':
                is_cash = True
            else:
                is_cash = False

            Position.objects.create(
                account_number=portfolio_link,
                isin=fund_link,
                value=float(
                    new_position['Base Market Value'].replace(',', '')),
                shares=float(
                    new_position['Shares/Par Value'].replace(",", '')),
                price=new_position['Base Price Amount'],
                valuation_date=new_position['Period End Date'],
                flag_cash=is_cash)
