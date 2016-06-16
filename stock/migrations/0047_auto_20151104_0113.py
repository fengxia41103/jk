# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0046_mysector_stocks'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystockhistorical',
            name='cci',
            field=models.FloatField(
                null=True, verbose_name='CCI indicator', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystockhistorical',
            name='decycler_oscillator',
            field=models.FloatField(
                null=True, verbose_name='Decycler oscillator', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystockhistorical',
            name='lg_slope',
            field=models.FloatField(
                null=True, verbose_name='Linear regression slope', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystockhistorical',
            name='si',
            field=models.FloatField(
                null=True, verbose_name='SI indicator', blank=True),
            preserve_default=True,
        ),
    ]
