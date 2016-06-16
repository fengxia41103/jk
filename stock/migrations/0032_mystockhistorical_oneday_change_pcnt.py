# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0031_auto_20151019_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystockhistorical',
            name='oneday_change_pcnt',
            field=models.FloatField(
                null=True, verbose_name="(Today's Open - PrevDay's Adj Close)/Adj close*100", blank=True),
            preserve_default=True,
        ),
    ]
