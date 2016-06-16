# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0006_auto_20150709_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mystock',
            name='vol',
            field=models.FloatField(
                default=0.0, verbose_name='Volume (in 000)'),
            preserve_default=True,
        ),
    ]
