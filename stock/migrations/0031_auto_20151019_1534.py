# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0030_auto_20151018_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='myposition',
            name='close_date',
            field=models.DateField(null=True, verbose_name='Position close date', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myposition',
            name='open_date',
            field=models.DateField(null=True, verbose_name='Position open date', blank=True),
            preserve_default=True,
        ),
    ]
