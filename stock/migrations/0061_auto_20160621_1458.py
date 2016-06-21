# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0060_auto_20160620_2339'),
    ]

    operations = [
        migrations.AddField(
            model_name='myposition',
            name='cost',
            field=models.DecimalField(default=0.0, verbose_name='Cost', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myposition',
            name='gain',
            field=models.DecimalField(default=0.0, verbose_name='Gain', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mysimulationsnapshot',
            name='gain_from_exit',
            field=models.DecimalField(default=0, verbose_name='Gain from exit', max_digits=20, decimal_places=4),
            preserve_default=True,
        ),
    ]
