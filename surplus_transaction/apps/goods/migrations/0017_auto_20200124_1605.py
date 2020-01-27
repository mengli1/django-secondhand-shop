# Generated by Django 2.2.5 on 2020-01-24 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0016_auto_20200122_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='fineness',
            field=models.SmallIntegerField(choices=[(0, '全新'), (1, '9成新'), (2, '8成新'), (3, '7成新及以下')], default=0, verbose_name='商品成色'),
        ),
    ]
