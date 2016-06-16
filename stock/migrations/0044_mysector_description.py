# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0043_mysector'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysector',
            name='description',
            field=models.TextField(
                null=True, verbose_name='Description', blank=True),
            preserve_default=True,
        ),
    ]
