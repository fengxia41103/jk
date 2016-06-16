# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0036_auto_20151024_1628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myposition',
            name='close_position',
            field=models.DecimalField(
                default=0.0, verbose_name='We closed at', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='ask',
            field=models.DecimalField(
                default=0.0, verbose_name='Ask price', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='bid',
            field=models.DecimalField(
                default=0.0, verbose_name='Bid price', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='day_high',
            field=models.DecimalField(
                default=0.0, verbose_name='Day high', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='day_low',
            field=models.DecimalField(
                default=0.0, verbose_name='Day low', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='day_open',
            field=models.DecimalField(
                default=0.0, verbose_name='Today opening price', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='last',
            field=models.DecimalField(
                default=0.0, verbose_name='Spot price', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='pe',
            field=models.DecimalField(
                default=0.0, verbose_name='P/E', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='prev_close',
            field=models.DecimalField(
                default=0.0, verbose_name='Prev day closing price', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='prev_high',
            field=models.DecimalField(
                default=0.0, verbose_name='Prev day highest price', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='prev_low',
            field=models.DecimalField(
                default=0.0, verbose_name='Prev day lowest price', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='prev_open',
            field=models.DecimalField(
                default=0.0, verbose_name='Prev day opening price', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystock',
            name='spread',
            field=models.DecimalField(
                default=0.0, verbose_name='Bid-ask spread', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='adj_close',
            field=models.DecimalField(
                default=-1, verbose_name='Adjusted close', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='adj_high',
            field=models.DecimalField(
                default=-1, verbose_name='Adjusted high', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='adj_low',
            field=models.DecimalField(
                default=-1, verbose_name='Adjusted low', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='adj_open',
            field=models.DecimalField(
                default=-1, verbose_name='Adjusted open', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='close_price',
            field=models.DecimalField(
                verbose_name='Close', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='high_price',
            field=models.DecimalField(
                verbose_name='High', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='low_price',
            field=models.DecimalField(
                verbose_name='Low', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='mystockhistorical',
            name='open_price',
            field=models.DecimalField(
                verbose_name='Open', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='myuserprofile',
            name='per_trade_total',
            field=models.DecimalField(
                default=1000.0, verbose_name='Per trade dollar amount', max_digits=20, decimal_places=5),
            preserve_default=True,
        ),
    ]
