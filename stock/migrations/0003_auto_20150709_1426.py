# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0002_auto_20150709_1404'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mystock',
            old_name='spot',
            new_name='last',
        ),
        migrations.RenameField(
            model_name='mystock',
            old_name='spot_time',
            new_name='last_update_time',
        ),
    ]
