# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0037_auto_20151026_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystock',
            name='is_china_stock',
            field=models.BooleanField(default=False, verbose_name=b'Is a China stock'),
            preserve_default=True,
        ),
    ]
