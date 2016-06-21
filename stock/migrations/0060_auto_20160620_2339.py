# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0059_auto_20160619_1303'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mysimulationsnapshot',
            name='asset_cumulative_gain_pcnt',
        ),
        migrations.AddField(
            model_name='mysimulationsnapshot',
            name='asset_gain_pcnt_t0',
            field=models.FloatField(default=0, help_text="This measures asset return in pcnt comparing to T0's", verbose_name='Asset gain from T0'),
            preserve_default=True,
        ),
    ]
