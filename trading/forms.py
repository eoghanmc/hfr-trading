import io
import csv
import trading

from django import forms
from .models import Fund, Portfolio, Position
from django.core.validators import ValidationError


class GenerateTradesForm(forms.Form):

    # Fields (inputs)
    account = forms.ModelChoiceField(queryset=None)
    trade_date = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    net_flows = forms.FloatField()
    trade_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=(
            ('Cash', 'Cash'), ('Rebalance', 'Rebalance'), ('Both', 'Both')))
    target_weights_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Portfolio.objects.all()

    def clean_net_flows(self):
        data = self.cleaned_data['net_flows']
        acct = self.cleaned_data['account']
        portfolio_sum = float(Portfolio.objects.get(account_number=acct)
                              .get_position_sum())

        # Check if net flows is redemption (i.e. < 0) AND
        # if larger than portfolio sum (cannot redeem more funds than total)
        if (data < 0) and (abs(data) > portfolio_sum):
            raise ValidationError(
                'Redemption amount is greater than the portfolio total')

        # Remember to always return the cleaned data.
        return data

    def read_target_weights(self):
        f = io.TextIOWrapper(self.check_file_csv().file)
        reader = csv.DictReader(f)

        data = []
        for line_position in reader:
            target_position = dict(line_position)
            data = data.append({
                "index_isin": target_position['ISIN'],
                "target_weight": target_position['Weight']})

        return data

    def check_file_csv(self):
        f = self.cleaned_data['file']
        if f:
            ext = f.name.split('.')[-1]
            if ext != 'csv':
                raise forms.ValidationError('File type not supported')
        return f

    def process_data(self):
        portfolio = self.cleaned_data['account']
        trade_type = self.cleaned_data['trade_type']
        trade_amount = self.cleaned_data['net_flows']
        trade_date = self.cleaned_data['trade_date']
        rebalance_weights = self.read_target_weights()

        # Get fund info - get all funds that have Index ISINd that match
        # what is in the rbalance_weights data

        # Get the current portfolio from what is already stored in Position set
        positions = portfolio.position_set.all()

        # Generate Trades here - returned as dict()
        sim_trades = trading.calculate_trades(
            portfolio, positions, rebalance_weights,
            trade_type, trade_amount, trade_date)

        # Return trading data
        return sim_trades


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
