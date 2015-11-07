# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0049_auto_20151105_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystockhistorical',
            name='relative_ma',
            field=models.FloatField(null=True, verbose_name='Relative Position Moving Average', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mysimulationcondition',
            name='strategy_value',
            field=models.IntegerField(default=1, verbose_name='Strategy value', choices=[(1, b'Daily return'), (2, b'Relative (H,L)'), (3, b'Relative Moving Avg')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='relative_hl',
            field=models.FloatField(null=True, verbose_name='Relative Position (H,L)', blank=True),
            preserve_default=True,
        ),
    ]
