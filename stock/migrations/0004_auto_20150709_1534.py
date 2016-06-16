# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0003_auto_20150709_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mystock',
            name='last_update_time',
            field=models.DateTimeField(
                auto_now=True, verbose_name='Spot sample time', null=True),
            preserve_default=True,
        ),
    ]
