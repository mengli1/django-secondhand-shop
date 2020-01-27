# Generated by Django 2.2.5 on 2020-01-21 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0008_auto_20200121_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='fineness',
            field=models.SmallIntegerField(choices=[(3, '7成新及以下'), (0, '全新'), (1, '9成新'), (2, '8成新')], default=0, verbose_name='商品成色'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='status',
            field=models.SmallIntegerField(choices=[(0, '未售出'), (1, '已售出')], default=0, verbose_name='商品状态'),
        ),
    ]