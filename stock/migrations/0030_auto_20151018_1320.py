# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0029_auto_20151018_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuserprofile',
            name='cash',
            field=models.DecimalField(default=10000, verbose_name='Account balance', max_digits=20, decimal_places=2),
            preserve_default=True,
        ),
    ]
