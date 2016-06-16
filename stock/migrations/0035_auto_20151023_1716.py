# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0034_auto_20151022_1951'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mystockhistorical',
            name='oneday_change_pcnt',
        ),
        migrations.AddField(
            model_name='mystockhistorical',
            name='oneday_change',
            field=models.FloatField(
                null=True, verbose_name="(Today's Open - Prev close)/prev close*100", blank=True),
            preserve_default=True,
        ),
    ]
