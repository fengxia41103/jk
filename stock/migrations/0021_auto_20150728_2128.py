# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0020_auto_20150728_1757'),
    ]

    operations = [
        migrations.RenameField(
            model_name='myuserprofile',
            old_name='balance',
            new_name='cash',
        ),
    ]
