# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0045_auto_20151103_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysector',
            name='stocks',
            field=models.ManyToManyField(to='stock.MyStock'),
            preserve_default=True,
        ),
    ]
