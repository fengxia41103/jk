# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0058_auto_20160619_0609'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MyChenmin',
        ),
        migrations.RemoveField(
            model_name='mysimulationresult',
            name='condition',
        ),
        migrations.DeleteModel(
            name='MySimulationResult',
        ),
        migrations.RemoveField(
            model_name='mysimulationsnapshot',
            name='gain_from_exit',
        ),
        migrations.AddField(
            model_name='myposition',
            name='life_in_days',
            field=models.IntegerField(default=0, verbose_name='Life in days'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mysimulationsnapshot',
            name='asset_cumulative_gain_pcnt',
            field=models.FloatField(default=0, help_text="This measures asset return in pcnt comparing to T0's", verbose_name='Asset cumulative return'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mysimulationsnapshot',
            name='asset_gain_pcnt',
            field=models.FloatField(default=0, help_text='This measures asset return in pcnt comparing to previous day', verbose_name='Asset gain from previous day'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mysimulationsnapshot',
            name='asset',
            field=models.DecimalField(default=0, verbose_name='Asset', max_digits=20, decimal_places=4),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mysimulationsnapshot',
            name='cash',
            field=models.DecimalField(default=0, verbose_name='Cash', max_digits=20, decimal_places=4),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mysimulationsnapshot',
            name='equity',
            field=models.DecimalField(default=0, verbose_name='Equity', max_digits=20, decimal_places=4),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mysimulationsnapshot',
            name='gain_from_holding',
            field=models.DecimalField(default=0, verbose_name='Gain from holding', max_digits=20, decimal_places=4),
            preserve_default=True,
        ),
    ]
