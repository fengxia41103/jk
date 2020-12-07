import os
import os.path
import sys
from datetime import date
from itertools import chain

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils.dateparse import parse_date

from stock.utility import MyBatchHandler
from stock.utility import MyUtility


class Command(BaseCommand):
    help = 'Run simulation using sliding window'

    def add_arguments(self, parser):
        parser.add_argument('start',
                            help="Start date")
        parser.add_argument('end',
                            help="End date")

        parser.add_argument('window',
                            type=int,
                            help="Sliding window (days)")

    def handle(self, *args, **options):
        self.stdout.write(os.path.dirname(__file__),
                          ending='')

        sliding_windows = MyUtility.sliding_windows(
            parse_date(options["start"]),
            parse_date(options["end"]),
            options.get("window", 10)
        )

        MyBatchHandler.batch_simulation_daily_return(
            date_range=sliding_windows,
            strategies=[2, 3],
            capital=10000,
            per_trade=1000)
