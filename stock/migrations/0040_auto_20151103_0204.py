# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0039_auto_20151103_0124'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mystock',
            name='float_share',
        ),
        migrations.AddField(
            model_name='mystock',
            name='floating_share',
            field=models.FloatField(default=0.0, verbose_name='Floating share(in million)'),
            preserve_default=True,
        ),
    ]
