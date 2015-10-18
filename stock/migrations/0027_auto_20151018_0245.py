# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0026_mystockhistorical_peer_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myposition',
            name='vol',
            field=models.FloatField(default=0, verbose_name='Trade vol'),
            preserve_default=True,
        ),
    ]
