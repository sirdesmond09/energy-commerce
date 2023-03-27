# Generated by Django 3.2.2 on 2023-02-24 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_auto_20230224_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cancel_requested_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='cancel_responded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='cancel_requested_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='cancel_responded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
