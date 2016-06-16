# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0008_auto_20150709_1806'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyPosition',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('position', models.DecimalField(
                    verbose_name='We paid', max_digits=20, decimal_places=15)),
                ('exit_bid', models.DecimalField(
                    verbose_name='Sell at', max_digits=20, decimal_places=15)),
                ('vol', models.IntegerField(default=0, verbose_name='Trade vol')),
                ('is_open', models.BooleanField(
                    default=True, verbose_name='Is position open')),
                ('last_updated_on', models.DateTimeField(auto_now=True)),
                ('stock', models.ForeignKey(verbose_name='Stock', to='stock.MyStock')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='mytrade',
            name='stock',
        ),
        migrations.DeleteModel(
            name='MyTrade',
        ),
        migrations.RemoveField(
            model_name='mystock',
            name='day_range',
        ),
        migrations.AddField(
            model_name='mystock',
            name='day_high',
            field=models.DecimalField(
                default=0.0, verbose_name='Day high', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mystock',
            name='day_low',
            field=models.DecimalField(
                default=0.0, verbose_name='Day low', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='is_in_play',
            field=models.BooleanField(
                default=False, verbose_name='Has pending position'),
            preserve_default=True,
        ),
    ]
