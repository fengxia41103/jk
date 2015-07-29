# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0019_auto_20150728_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystock',
            name='fib_daily_score',
            field=models.FloatField(default=0, verbose_name='Weighed sum of daily adj close price'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='fib_weekly_score',
            field=models.FloatField(default=0, verbose_name='Weighed sum of weekly adj close price'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myposition',
            name='close_position',
            field=models.DecimalField(default=0.0, verbose_name='We closed at', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
    ]
