# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0022_mystockhistorical_flag_by_strategy'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='mystockhistorical',
            unique_together=set([('stock', 'date_stamp')]),
        ),
        migrations.AlterIndexTogether(
            name='mystockhistorical',
            index_together=set([('stock', 'date_stamp')]),
        ),
    ]
