# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('name', models.CharField(default=b'default name',
                                          max_length=64, verbose_name='\u9644\u4ef6\u540d\u79f0')),
                ('description', models.CharField(default=b'default description',
                                                 max_length=64, verbose_name='\u9644\u4ef6\u63cf\u8ff0')),
                ('file', models.FileField(help_text='\u9644\u4ef6',
                                          upload_to=b'%Y/%m/%d', verbose_name='\u9644\u4ef6')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL,
                                                 blank=True, help_text=b'', null=True, verbose_name='\u521b\u5efa\u7528\u6237')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyStock',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('company_name', models.CharField(max_length=128,
                                                  null=True, verbose_name='Company name', blank=True)),
                ('symbol', models.CharField(max_length=8, verbose_name='Stock symbol')),
                ('prev_close', models.DecimalField(
                    default=0.0, verbose_name='Prev day closing price', max_digits=20, decimal_places=15)),
                ('prev_open', models.DecimalField(
                    default=0.0, verbose_name='Prev day opening price', max_digits=20, decimal_places=15)),
                ('today_open', models.DecimalField(
                    default=0.0, verbose_name='Today opening price', max_digits=20, decimal_places=15)),
                ('pe', models.DecimalField(default=0.0,
                                           verbose_name='P/E', max_digits=20, decimal_places=15)),
                ('spot', models.DecimalField(default=0.0,
                                             verbose_name='Spot price', max_digits=20, decimal_places=15)),
                ('spot_time', models.DateTimeField(null=True,
                                                   verbose_name='Spot sample time', blank=True)),
                ('is_in_play', models.BooleanField(
                    default=False, verbose_name='Has pending exit')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyTaggedItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.SlugField(default=b'',
                                         max_length=16, verbose_name='Tag')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyTrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('exit', models.DecimalField(
                    verbose_name='Exit price', max_digits=20, decimal_places=15)),
                ('stock', models.ForeignKey(verbose_name='Stock', to='stock.MyStock')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyUserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('per_trade_total', models.DecimalField(default=1000.0,
                                                        verbose_name='Per trade dollar amount', max_digits=20, decimal_places=15)),
                ('pe_threshold', models.CharField(default=b'20-100',
                                                  max_length=16, verbose_name='P/E threshold')),
                ('exit_percent', models.IntegerField(default=2,
                                                     verbose_name='Percentage of exit over buy-in price')),
                ('owner', models.OneToOneField(default=None, to=settings.AUTH_USER_MODEL,
                                               help_text=b'', verbose_name='\u7528\u6237')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
