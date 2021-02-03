import os
import os.path
import sys
from datetime import date
from itertools import chain

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_date

from stock.models import MyStock
from stock.tasks import (
    backtesting_cci_consumer,
    backtesting_daily_return_consumer,
    backtesting_decycler_oscillator_consumer,
    backtesting_linear_slope_consumer,
    backtesting_relative_hl_consumer,
    backtesting_relative_ma_consumer,
    backtesting_s1_consumer,
    backtesting_si_consumer,
)


class Command(BaseCommand):
    help = "Compute derived meta values such as daily return, relative HL."

    def add_arguments(self, parser):
        parser.add_argument("symbol", help="Symbol or ALL")

    def handle(self, *args, **options):
        self.stdout.write(os.path.dirname(__file__), ending="")

        candidate = options["symbol"].lower()
        if candidate == "all":
            symbols = MyStock.objects.values_list("symbol", flat=True)
        else:
            symbols = [candidate]

        for s in symbols:
            backtesting_daily_return_consumer.delay(s)
            backtesting_s1_consumer.delay(s)
            backtesting_cci_consumer.delay(s)
            backtesting_decycler_oscillator_consumer.delay(s)
            backtesting_linear_slope_consumer.delay(s)
            backtesting_relative_hl_consumer.delay(s)
            backtesting_relative_ma_consumer.delay(s)
            backtesting_si_consumer.delay(s)
