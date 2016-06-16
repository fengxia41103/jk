# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0035_auto_20151023_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystockhistorical',
            name='adj_factor',
            field=models.FloatField(
                default=0, verbose_name='Adjustment factor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystockhistorical',
            name='adj_high',
            field=models.DecimalField(
                default=-1, verbose_name='Adjusted high', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystockhistorical',
            name='adj_low',
            field=models.DecimalField(
                default=-1, verbose_name='Adjusted low', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystockhistorical',
            name='adj_open',
            field=models.DecimalField(
                default=-1, verbose_name='Adjusted open', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystockhistorical',
            name='amount',
            field=models.FloatField(
                default=-1, verbose_name='\u6210\u4ea4\u91d1\u989d (000)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystockhistorical',
            name='status',
            field=models.IntegerField(
                default=-1, verbose_name='Stock trading status, eg. stopped trading on that day'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='adj_close',
            field=models.DecimalField(
                default=-1, verbose_name='Adjusted close', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
    ]
