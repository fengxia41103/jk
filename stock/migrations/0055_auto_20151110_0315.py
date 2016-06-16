# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0054_auto_20151108_1555'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='mysimulationcondition',
            unique_together=set([('data_source', 'sector', 'strategy', 'strategy_value', 'data_sort',
                                  'start', 'end', 'capital', 'per_trade', 'buy_cutoff', 'sell_cutoff')]),
        ),
    ]
