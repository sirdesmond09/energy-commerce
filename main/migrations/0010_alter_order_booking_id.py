# Generated by Django 3.2.2 on 2023-02-15 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20230213_0923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='booking_id',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
