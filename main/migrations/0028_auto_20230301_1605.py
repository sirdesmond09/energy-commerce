# Generated by Django 3.2.2 on 2023-03-01 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_orderitem_installation_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='max_order_qty',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='product_sku',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='productcomponent',
            name='unit',
            field=models.CharField(max_length=255, null=True),
        ),
    ]