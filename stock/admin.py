from django.contrib import admin

from stock.models import *


# Register your models here.


class MyStockAdmin(admin.ModelAdmin):
    list_filter = ['is_sp500', 'is_in_play', 'is_composite']
    list_display = ('company_name', 'symbol')


admin.site.register(MyStock, MyStockAdmin)
