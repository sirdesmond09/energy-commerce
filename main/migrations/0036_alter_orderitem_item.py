# Generated by Django 3.2.2 on 2023-03-07 13:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_alter_orderitem_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='order_items', to='main.product'),
        ),
    ]
