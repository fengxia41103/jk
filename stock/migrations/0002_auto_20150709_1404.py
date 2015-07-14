# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystock',
            name='prev_high',
            field=models.DecimalField(default=0.0, verbose_name='Prev day highest price', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='prev_low',
            field=models.DecimalField(default=0.0, verbose_name='Prev day lowest price', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='prev_vol',
            field=models.IntegerField(default=0, verbose_name='Prev day volume'),
            preserve_default=True,
        ),
    ]
