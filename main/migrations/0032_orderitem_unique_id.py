# Generated by Django 3.2.2 on 2023-03-04 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_product_locations'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='unique_id',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
