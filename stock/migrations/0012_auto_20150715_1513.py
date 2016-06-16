# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0011_auto_20150714_1831'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystock',
            name='month_adjusted_close',
            field=models.TextField(
                default=b'', verbose_name='1-month adjusted closing price'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='week_adjusted_close',
            field=models.TextField(
                default=b'', verbose_name='1-week adjusted closing price'),
            preserve_default=True,
        ),
    ]
