# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0053_auto_20151106_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysimulationcondition',
            name='sector',
            field=models.ForeignKey(default=None, blank=True, to='stock.MySector', null=True, verbose_name='Data source sector'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mysimulationcondition',
            name='data_source',
            field=models.IntegerField(default=1, choices=[(1, b'S&P500'), (2, b'CI00*'), (3, b'WIND 8821*'), (4, b'China stock'), (5, b'WIND 2nd-tier sector')]),
            preserve_default=True,
        ),
    ]
