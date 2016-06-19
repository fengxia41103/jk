# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0057_mystockhistorical_overnight_return'),
    ]

    operations = [
        migrations.CreateModel(
            name='MySimulationSnapshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('on_date', models.DateField(default=b'2014-01-01', verbose_name='Snapshot date')),
                ('cash', models.DecimalField(verbose_name='Cash', max_digits=20, decimal_places=4)),
                ('equity', models.DecimalField(verbose_name='Equity', max_digits=20, decimal_places=4)),
                ('asset', models.DecimalField(verbose_name='Asset', max_digits=20, decimal_places=4)),
                ('gain_from_exit', models.DecimalField(verbose_name='Gain from exit', max_digits=20, decimal_places=4)),
                ('gain_from_holding', models.DecimalField(verbose_name='Gain from holding', max_digits=20, decimal_places=4)),
                ('simulation', models.ForeignKey(to='stock.MySimulationCondition')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='myposition',
            name='close_date',
            field=models.DateField(default=None, null=True, verbose_name='Position close date', blank=True),
            preserve_default=True,
        ),
    ]
