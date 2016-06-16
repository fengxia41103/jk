# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0009_auto_20150709_1841'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystock',
            name='prev_change',
            field=models.FloatField(
                default=0.0, verbose_name='Prev day change (%)'),
            preserve_default=True,
        ),
    ]
