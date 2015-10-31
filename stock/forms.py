from django import forms
from django.contrib.admin.widgets import AdminDateWidget
import datetime as dt

DATA_CHOICES = (
    (1, "S&P500"),
    (2, "China sector"),
    (3, "China stock"),    
)
DATA_SORT_CHOICES = (       
    (0, "ascending"),
    (1, "descending"),
)

class HistoricalListForm(forms.Form):
    data_source = forms.ChoiceField(
        choices = DATA_CHOICES,
        initial = 1
    )        
    on_date = forms.DateField(
        initial = "2014-01-01",
        label = 'On date',
        widget = AdminDateWidget,        
    )

class StrategyControlForm(forms.Form):
    STRATEGY_CHOICES = (
        (1, "S1 (by ranking)"),
        (2, "S2 (buy low sell high)"),
    )
    data_source = forms.ChoiceField(
        choices = DATA_CHOICES,
        initial = 1
    )    
    strategy = forms.ChoiceField(
        choices = STRATEGY_CHOICES,
        initial = 1
    )
    data_sort = forms.ChoiceField(
        choices = DATA_SORT_CHOICES,
        initial = 2,
        label = "Sort order"
    )
    start = forms.DateField (
    	initial = "2014-01-01",
        label = 'Start date',
    	widget = AdminDateWidget,
    )
    end = forms.DateField (
    	initial = "2014-01-10",
        label = 'End date',
    	widget = AdminDateWidget
    )
    capital = forms.IntegerField(
    	initial = 10000,
        label = "Starting cash"
    )    
    buy_cutoff = forms.FloatField(
    	initial = 25,
        max_value = 100,
        min_value = 0,
        label = "Buy cutoff (%)"
    )
    sell_cutoff = forms.FloatField(
    	initial = 75,
        max_value = 100,
        min_value = 0,
        label = "Sell cutoff (%)"
    )    
