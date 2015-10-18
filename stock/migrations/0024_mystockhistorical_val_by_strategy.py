# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0023_auto_20151016_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystockhistorical',
            name='val_by_strategy',
            field=models.FloatField(default=0.0, null=True, verbose_name=b'Computed value based on a strategy', blank=True),
            preserve_default=True,
        ),
    ]
