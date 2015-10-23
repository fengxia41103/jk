# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0027_auto_20151018_0245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myposition',
            name='vol',
            field=models.DecimalField(default=0, verbose_name='Trade vol', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
    ]