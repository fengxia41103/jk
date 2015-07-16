# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0015_mychenmin_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mystock',
            name='fib_adjusted_close',
        ),
        migrations.AddField(
            model_name='mystock',
            name='fib_daily_adjusted_close',
            field=models.TextField(default=b'', verbose_name='Fibonacci timezone adjusted closing price'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='fib_weekly_adjusted_close',
            field=models.TextField(default=b'', verbose_name='Fibonacci timezone adjusted closing price'),
            preserve_default=True,
        ),
    ]
