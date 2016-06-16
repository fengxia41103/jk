# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0048_mysimulationcondition_mysimulationresult'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myposition',
            name='category',
        ),
        migrations.AddField(
            model_name='myposition',
            name='simulation',
            field=models.ForeignKey(
                default=None, to='stock.MySimulationCondition'),
            preserve_default=False,
        ),
    ]
