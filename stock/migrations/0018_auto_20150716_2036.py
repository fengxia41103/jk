# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0017_mystockhistorical'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mystockhistorical',
            old_name='datestamp',
            new_name='date_stamp',
        ),
    ]
