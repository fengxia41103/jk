from django import forms
from django.contrib.admin.widgets import AdminDateWidget
import datetime as dt

class DateSelectionForm(forms.Form):
    start = forms.DateField (
    	initial = "2014-01-01",
    	widget = AdminDateWidget
    )
    end = forms.DateField (
    	initial = "2014-01-10",
    	widget = AdminDateWidget
    )
    capital = forms.IntegerField(
    	initial = 50000
    )    
    buy_cutoff = forms.FloatField(
    	initial = 0.25
    )
    sell_cutoff = forms.FloatField(
    	initial = 0.75
    )    
