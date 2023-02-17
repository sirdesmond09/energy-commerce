# Generated by Django 3.2.2 on 2023-02-17 10:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20230217_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='primary_img',
            field=models.ImageField(blank=True, upload_to='products/primary_imgs', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])]),
        ),
    ]
