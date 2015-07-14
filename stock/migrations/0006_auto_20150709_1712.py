# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0005_auto_20150709_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mystock',
            name='float_share',
            field=models.FloatField(default=0.0, verbose_name='Float share(in million)'),
            preserve_default=True,
        ),
    ]
