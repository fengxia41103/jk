# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0010_mystock_prev_change'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystock',
            name='day_change',
            field=models.FloatField(
                default=0.0, verbose_name='Today change(%)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='spread',
            field=models.DecimalField(
                default=0.0, verbose_name='Bid-ask spread', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='vol_over_float',
            field=models.FloatField(
                default=0.0, verbose_name='Vol/floating shares (%)'),
            preserve_default=True,
        ),
    ]
