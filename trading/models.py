from django.db import models
from django.urls import reverse_lazy
from datetime import time
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime


STATUSES = (
    ("Active", "Active"),
    ("Inactive", "Inactive"),
)


class Portfolio(models.Model):
    # Fields
    status = models.CharField(max_length=200, choices=STATUSES,
                              default='Active', blank=False)
    account_number = models.CharField(max_length=200, primary_key=True,
                                      unique=True, blank=False)
    name = models.CharField(max_length=200, blank=False)
    guideline_shares_owned = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ]
    )
    guideline_assets_owned = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ]
    )
    guideline_max_weight = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ]
    )

    # Methods
    def get_absolute_url(self):
        """Returns the url to access a particular instance of Fund."""
        return reverse_lazy('portfolio-detail', args=[str(self.pk)])

    def __str__(self):
        return self.account_number


class Fund(models.Model):

    STYLES = (
        ("Equity Hedge", "Equity Hedge"),
        ("Event Driven", "Event Driven"),
        ("Global Macro", "Global Macro"),
        ("Relative Value", "Relative Value"),
    )

    STRATEGIES = (
        ("Equity Long/Short", "Equity Long/Short"),
        ("Equity Market Neutral", "Equity Market Neutral"),
        ("Equity Long Bias", "Equity Long Bias"),
        ("Activist", "Activist"),
        ("Value-wth-catalyst", "Value-with-catalyst"),
        ("ED Multi Strategy", "ED Multi Strategy"),
    )

    # Fields
    status = models.CharField(max_length=200, choices=STATUSES,
                              default='Active', blank=False)
    isin = models.CharField(max_length=200, primary_key=True, unique=True,
                            blank=False)
    index_isin = models.CharField(max_length=200, blank=False)
    name = models.CharField(max_length=200, blank=False)
    firm = models.CharField(max_length=200, blank=False)
    style = models.CharField(max_length=200, choices=STYLES, blank=False)
    strategy = models.CharField(max_length=200, choices=STRATEGIES,
                                blank=False)
    flag_restricted = models.BooleanField(default=False)
    flag_late_cutoff = models.BooleanField(default=False)
    flag_units_trading = models.BooleanField(default=False)
    terms_rank = models.PositiveSmallIntegerField(default=1)
    terms_rank_amount = models.PositiveIntegerField()
    terms_sub_notice = models.PositiveSmallIntegerField()
    terms_sub_settlement = models.PositiveSmallIntegerField()
    terms_sub_minimum = models.PositiveIntegerField()
    terms_red_notice = models.PositiveSmallIntegerField()
    terms_red_settlement = models.PositiveSmallIntegerField()
    terms_cutoff_time = models.TimeField(default=time(17, 30))
    terms_calendars = models.CharField(max_length=500, default='')
    terms_man_fee = models.DecimalField(max_digits=6, decimal_places=5)
    terms_perf_fee = models.DecimalField(max_digits=6, decimal_places=5)
    terms_currency = models.CharField(max_length=3, default='USD', blank=False)

    # Methods
    def get_absolute_url(self):
        """Returns the url to access a particular instance of Fund."""
        return reverse_lazy('fund-detail', args=[str(self.pk)])

    def __str__(self):
        return self.isin


class Position(models.Model):
    """
    Class/ORM for every past/current/future position (uploaded via file)
    """

    # Fields
    id = models.AutoField(primary_key=True, editable=False)
    account_number = models.ForeignKey('Portfolio', on_delete=models.SET_NULL,
                                       null=True)
    isin = models.ForeignKey('Fund', on_delete=models.SET_NULL,
                             null=True)
    flag_cash = models.BooleanField(default=False)
    value = models.FloatField()
    shares = models.FloatField()
    price = models.FloatField()
    valuation_date = models.DateField(blank=False, default=datetime.date.today)

    # Methods
    def __str__(self):
        return self.id


class TradeItem(models.Model):
    """
    Class/ORM for every trade line item generated
    """

    # Fields
    id = models.AutoField(primary_key=True, editable=False)
    account_number = models.ForeignKey('Portfolio', on_delete=models.SET_NULL,
                                       null=True)
    isin = models.ForeignKey('Fund', on_delete=models.SET_NULL,
                             null=True)
    notice_date = models.DateField()
    trade_date = models.DateField()
    settlement_date = models.DateField()
    traded_amount = models.FloatField()
    traded_shares = models.FloatField()
    trade_note = models.TextField()
    breaches = models.TextField()

    # Methods

    def __str__(self):
        return self.id


class BBGData(models.Model):
    """
    Class/ORM for bloomberg data that is uploaded separately
    """

    # Fields
    id = models.AutoField(primary_key=True, editable=False)
    isin = models.ForeignKey('Fund', on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    assets = models.FloatField()
    shares_issued = models.FloatField()

    # Methods
    def __str__(self):
        return self.id
