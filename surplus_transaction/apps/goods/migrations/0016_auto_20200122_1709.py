# Generated by Django 2.2.5 on 2020-01-22 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0015_auto_20200121_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='fineness',
            field=models.SmallIntegerField(choices=[(1, '9成新'), (3, '7成新及以下'), (2, '8成新'), (0, '全新')], default=0, verbose_name='商品成色'),
        ),
    ]
