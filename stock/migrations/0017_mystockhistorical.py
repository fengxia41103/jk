# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0016_auto_20150716_1917'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyStockHistorical',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('datestamp', models.DateField(verbose_name='Date')),
                ('open_price', models.DecimalField(
                    verbose_name='Open', max_digits=20, decimal_places=15)),
                ('high_price', models.DecimalField(
                    verbose_name='High', max_digits=20, decimal_places=15)),
                ('low_price', models.DecimalField(
                    verbose_name='Low', max_digits=20, decimal_places=15)),
                ('close_price', models.DecimalField(
                    verbose_name='Close', max_digits=20, decimal_places=15)),
                ('adj_close', models.DecimalField(
                    verbose_name='Adjusted close', max_digits=20, decimal_places=15)),
                ('vol', models.FloatField(verbose_name='Volume (000)')),
                ('stock', models.ForeignKey(verbose_name='Stock', to='stock.MyStock')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
