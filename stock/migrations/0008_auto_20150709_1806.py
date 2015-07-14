# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0007_auto_20150709_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='mytrade',
            name='vol',
            field=models.IntegerField(default=0, verbose_name='Trade vol'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mytrade',
            name='exit',
            field=models.FloatField(verbose_name='Exit price'),
            preserve_default=True,
        ),
    ]
