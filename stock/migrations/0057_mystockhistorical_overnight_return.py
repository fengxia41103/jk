# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0056_auto_20160617_0352'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystockhistorical',
            name='overnight_return',
            field=models.FloatField(default=None, null=True, verbose_name="(Today's Open - Yesterday's adj close)/Yesterday's adj close*100", blank=True),
            preserve_default=True,
        ),
    ]
