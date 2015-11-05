# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0042_auto_20151103_0432'),
    ]

    operations = [
        migrations.CreateModel(
            name='MySector',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=8, verbose_name='Sector code')),
                ('source', models.CharField(max_length=32, verbose_name='Definition source')),
                ('parent', models.ForeignKey(default=None, blank=True, to='stock.MySector', null=True, verbose_name='Parent sector')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
