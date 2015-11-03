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
    STRATEGY_VALUE_CHOICES = (
        (1, "One day change %"),
        (2, "Two day change %"),
        (3, "Relative Position in (H,L)"),
        (4, 'Relative Position in Moving Average'),
        (5, 'CCI'),
        (6, 'SI'),
        (7, 'Linear Reg Slope'),
        (8, 'Decycler Oscillator'),
    )    
    data_source = forms.ChoiceField(
        choicesRelative Position indicator in (H,L) = DATA_CHOICES,
        initial = 1
    )
    strategy = forms.ChoiceField(
        choices = STRATEGY_CHOICES,
        initial = 1
    )
    strategy_value = forms.ChoiceField(
        choices = STRATEGY_VALUE_CHOICES,
        initial = 2,
        label = "Strategy value"
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
    	initial = 100000,
        label = "Starting cash"
    ) 
    per_trade = forms.IntegerField(
        initial = 10000,
        label = "Per trade amount"
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
