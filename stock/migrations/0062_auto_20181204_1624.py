# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0061_auto_20160621_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mystockhistorical',
            name='daily_return',
            field=models.FloatField(default=None, null=True, verbose_name="(Today's close - Today's Open)/Today's Open*100", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='overnight_return',
            field=models.FloatField(default=None, null=True, verbose_name="(Today's adj close - Yesterday's adj close)/Yesterday's adj close*100", blank=True),
            preserve_default=True,
        ),
    ]
