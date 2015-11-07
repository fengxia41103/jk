# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0052_auto_20151106_1457'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysimulationresult',
            name='snapshot',
            field=annoying.fields.JSONField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mysimulationresult',
            name='asset',
            field=annoying.fields.JSONField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mysimulationresult',
            name='cash',
            field=annoying.fields.JSONField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mysimulationresult',
            name='equity',
            field=annoying.fields.JSONField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mysimulationresult',
            name='on_dates',
            field=annoying.fields.JSONField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mysimulationresult',
            name='portfolio',
            field=annoying.fields.JSONField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mysimulationresult',
            name='transaction',
            field=annoying.fields.JSONField(),
            preserve_default=True,
        ),
    ]
