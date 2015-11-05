# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0047_auto_20151104_0113'),
    ]

    operations = [
        migrations.CreateModel(
            name='MySimulationCondition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_source', models.IntegerField(default=1, choices=[(1, b'S&P500'), (2, b'CI sector'), (3, b'WIND sector'), (4, b'China stock')])),
                ('strategy', models.IntegerField(default=1, choices=[(1, b'S1 (by ranking)'), (2, b'S2 (buy low sell high)')])),
                ('strategy_value', models.IntegerField(default=1, verbose_name='Strategy value', choices=[(1, b'Daily return'), (2, b'Relative (H,L)'), (3, b'Relative Moving Avg'), (4, b'CCI'), (5, b'SI'), (6, b'Linear Reg Slope'), (7, b'Decycler Oscillator')])),
                ('data_sort', models.IntegerField(default=2, verbose_name='Sort order', choices=[(0, b'ascending'), (1, b'descending')])),
                ('start', models.DateField(default=b'2014-01-01', verbose_name='Start date')),
                ('end', models.DateField(default=b'2014-01-10', verbose_name='End date')),
                ('capital', models.IntegerField(default=100000, verbose_name='Starting cash')),
                ('per_trade', models.IntegerField(default=10000, verbose_name='Per trade amount')),
                ('buy_cutoff', models.IntegerField(default=25, verbose_name=b'Buy cutoff (%)', validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
                ('sell_cutoff', models.IntegerField(default=75, verbose_name=b'Sell cutoff (%)', validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MySimulationResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
                ('result', models.TextField()),
                ('condition', models.OneToOneField(to='stock.MySimulationCondition')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
