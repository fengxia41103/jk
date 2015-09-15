# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0021_auto_20150728_2128'),
    ]

    operations = [
        migrations.AddField(
            model_name='mystockhistorical',
            name='flag_by_strategy',
            field=models.CharField(default=b'U', max_length=1, null=True, verbose_name='Back testing flag', blank=True),
            preserve_default=True,
        ),
    ]
