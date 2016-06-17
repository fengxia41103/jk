# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0055_auto_20151110_0315'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystock',
            name='is_index',
            field=models.BooleanField(default=False, help_text='Index is a derived value from basket of stocks', verbose_name='Is an index'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='cci',
            field=models.FloatField(default=None, null=True, verbose_name='CCI indicator', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='daily_return',
            field=models.FloatField(default=None, null=True, verbose_name="(Today's Close - Today's Open)/Today's Open*100", blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='decycler_oscillator',
            field=models.FloatField(default=None, null=True, verbose_name='Decycler oscillator', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='lg_slope',
            field=models.FloatField(default=None, null=True, verbose_name='Linear regression slope', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='relative_hl',
            field=models.FloatField(default=None, null=True, verbose_name='Relative Position (H,L)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='relative_ma',
            field=models.FloatField(default=None, null=True, verbose_name='Relative Position Moving Average', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='si',
            field=models.FloatField(default=None, null=True, verbose_name='SI indicator', blank=True),
            preserve_default=True,
        ),
    ]
