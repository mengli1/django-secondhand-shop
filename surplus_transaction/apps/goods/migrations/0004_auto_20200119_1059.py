# Generated by Django 2.2.5 on 2020-01-19 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0003_auto_20200118_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='fineness',
            field=models.SmallIntegerField(choices=[(1, '9成新'), (2, '8成新'), (0, '全新'), (3, '7成新及以下')], default=0, verbose_name='商品成色'),
        ),
    ]
