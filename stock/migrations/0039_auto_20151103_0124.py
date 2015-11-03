# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0038_mystock_is_china_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystockhistorical',
            name='twoday_change',
            field=models.FloatField(null=True, verbose_name="(Today's Close - Prev close)/prev close*100", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='oneday_change',
            field=models.FloatField(null=True, verbose_name="(Today's Close - Today's Open)/Today's Open*100", blank=True),
            preserve_default=True,
        ),
    ]
