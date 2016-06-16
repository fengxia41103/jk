# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0004_auto_20150709_1534'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mystock',
            old_name='today_open',
            new_name='day_open',
        ),
        migrations.AddField(
            model_name='mystock',
            name='ask',
            field=models.DecimalField(
                default=0.0, verbose_name='Ask price', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='bid',
            field=models.DecimalField(
                default=0.0, verbose_name='Bid price', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='day_range',
            field=models.CharField(
                max_length=64, null=True, verbose_name='Day range', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='float_share',
            field=models.IntegerField(default=0, verbose_name='Float share'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='vol',
            field=models.IntegerField(default=0, verbose_name='Volume'),
            preserve_default=True,
        ),
    ]
