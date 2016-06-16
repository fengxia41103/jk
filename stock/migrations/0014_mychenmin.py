# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0013_mystock_fib_adjusted_close'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyChenmin',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('executed_on', models.DateField(
                    verbose_name='\u53d1\u751f\u65e5\u671f')),
                ('symbol', models.CharField(max_length=32,
                                            verbose_name='\u8bc1\u5238\u4ee3\u7801')),
                ('transaction_type', models.CharField(
                    max_length=64, verbose_name='\u6458\u8981')),
                ('price', models.FloatField(verbose_name='\u6210\u4ea4\u4ef7\u683c')),
                ('vol', models.IntegerField(verbose_name='\u6210\u4ea4\u80a1\u6570')),
                ('total', models.IntegerField(
                    verbose_name='\u6210\u4ea4\u91d1\u989d')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
