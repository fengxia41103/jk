# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0024_mystockhistorical_val_by_strategy'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystock',
            name='is_sp500',
            field=models.BooleanField(default=False, verbose_name=b'Is a SP500 stock'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='sector',
            field=models.CharField(default=b'unknown', max_length=64, verbose_name=b'Sector name'),
            preserve_default=True,
        ),
    ]
