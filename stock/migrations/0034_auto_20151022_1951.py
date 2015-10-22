# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0033_myposition_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myposition',
            name='category',
            field=models.CharField(max_length=128, null=True, verbose_name='Category tag', blank=True),
            preserve_default=True,
        ),
    ]
