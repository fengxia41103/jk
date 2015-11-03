# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0041_auto_20151103_0410'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mystockhistorical',
            old_name='oneday_change',
            new_name='daily_return',
        ),
    ]
