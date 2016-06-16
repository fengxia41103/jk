# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0012_auto_20150715_1513'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystock',
            name='fib_adjusted_close',
            field=models.TextField(
                default=b'', verbose_name='Fib interval adjusted closing price'),
            preserve_default=True,
        ),
    ]
