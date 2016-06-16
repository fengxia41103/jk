# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0040_auto_20151103_0204'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mystockhistorical',
            name='twoday_change',
        ),
        migrations.AddField(
            model_name='mystockhistorical',
            name='relative_hl',
            field=models.FloatField(
                null=True, verbose_name='Relative Position indicator in (H,L)', blank=True),
            preserve_default=True,
        ),
    ]
