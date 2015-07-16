# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0014_mychenmin'),
    ]

    operations = [
        migrations.AddField(
            model_name='mychenmin',
            name='name',
            field=models.CharField(default=datetime.datetime(2015, 7, 16, 4, 40, 51, 159127, tzinfo=utc), max_length=32, verbose_name='\u8bc1\u5238\u540d\u79f0'),
            preserve_default=False,
        ),
    ]
