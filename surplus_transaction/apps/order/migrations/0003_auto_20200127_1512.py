# Generated by Django 2.2.5 on 2020-01-27 07:12

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20200124_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='comment',
            field=ckeditor_uploader.fields.RichTextUploadingField(default='', verbose_name='评论'),
        ),
    ]
