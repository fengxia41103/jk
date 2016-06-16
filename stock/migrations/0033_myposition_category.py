# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0032_mystockhistorical_oneday_change_pcnt'),
    ]

    operations = [
        migrations.AddField(
            model_name='myposition',
            name='category',
            field=models.CharField(
                max_length=16, null=True, verbose_name='Category tag', blank=True),
            preserve_default=True,
        ),
    ]
