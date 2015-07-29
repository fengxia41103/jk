# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stock', '0018_auto_20150716_2036'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myposition',
            name='exit_bid',
        ),
        migrations.RemoveField(
            model_name='myuserprofile',
            name='exit_percent',
        ),
        migrations.AddField(
            model_name='myposition',
            name='close_position',
            field=models.DecimalField(default=0, verbose_name='We closed at', max_digits=20, decimal_places=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='myposition',
            name='user',
            field=models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='myuserprofile',
            name='balance',
            field=models.DecimalField(default=10000, verbose_name='Account balance', max_digits=20, decimal_places=15),
            preserve_default=True,
        ),
    ]
