# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0051_auto_20151106_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysimulationresult',
            name='portfolio',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mysimulationresult',
            name='transaction',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
