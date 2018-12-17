from django.contrib import admin

from stock.models import *

# Register your models here.


class MyStockAdmin(admin.ModelAdmin):
    list_filter = ['is_sp500', 'is_china_stock', 'is_in_play', 'is_index']
    list_display = ('company_name', 'symbol', 'pe', 'day_open',
                    'day_low', 'day_high', 'last', 'is_in_play')
admin.site.register(MyStock, MyStockAdmin)


class MySimulationConditionAdmin(admin.ModelAdmin):
    list_display = ("data_source", "strategy", "data_sort", "start",
                    "end", "capital", "per_trade", "buy_cutoff", "sell_cutoff")

    list_filter = ("strategy", "buy_cutoff", "sell_cutoff")
admin.site.register(MySimulationCondition, MySimulationConditionAdmin)
