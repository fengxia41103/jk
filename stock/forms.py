from django import forms
from django.contrib.admin.widgets import AdminDateWidget
import datetime as dt

class DateSelectionForm(forms.Form):
    start = forms.DateField (
    	initial = "2015-01-01",
    	widget = AdminDateWidget
    )
    end = forms.DateField (
    	initial = "2015-01-10",
    	widget = AdminDateWidget
    )
