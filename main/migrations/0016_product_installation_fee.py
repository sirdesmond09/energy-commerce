# Generated by Django 3.2.2 on 2023-02-17 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_alter_product_primary_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='installation_fee',
            field=models.FloatField(default=0),
        ),
    ]