# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0050_auto_20151105_2154'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mysimulationresult',
            name='result',
        ),
        migrations.AddField(
            model_name='mysimulationresult',
            name='asset',
            field=models.TextField(default=datetime.datetime(
                2015, 11, 6, 14, 35, 35, 792378, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mysimulationresult',
            name='cash',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mysimulationresult',
            name='equity',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mysimulationresult',
            name='on_dates',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
