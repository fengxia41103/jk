# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0025_auto_20151017_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystockhistorical',
            name='peer_rank',
            field=models.IntegerField(default=0, null=True, verbose_name='Ranking among peers', blank=True),
            preserve_default=True,
        ),
    ]
