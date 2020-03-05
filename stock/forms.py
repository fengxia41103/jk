import datetime as dt

from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import ModelForm

from stock.models import *

DATA_CHOICES = (
    (1, "S&P500"),
    (2, "CI sector"),
    (3, "WIND sector"),
    (4, "China stock"),
)


class HistoricalListForm(forms.Form):
    data_source = forms.ChoiceField(
        choices=DATA_CHOICES,
        initial=1
    )
    on_date = forms.DateField(
        initial="2014-01-01",
        label='On date',
        widget=AdminDateWidget,
    )


class StrategyControlForm(ModelForm):

    class Meta:
        model = MySimulationCondition
        fields = '__all__'
