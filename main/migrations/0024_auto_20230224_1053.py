# Generated by Django 3.2.2 on 2023-02-24 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20230223_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cancellation_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='cancellation_response_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='prev_status',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='cancellation_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='cancellation_response_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='prev_status',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('pending', 'pending'), ('processing', 'processing'), ('completed', 'completed'), ('cancel-requested', 'cancel-requested'), ('user-canceled', 'user-canceled')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('confirmed', 'confirmed'), ('processing', 'processing'), ('in-transit', 'in-transit'), ('delivered', 'delivered'), ('cancel-requested', 'cancel-requested'), ('user-canceled', 'user-canceled')], default='pending', max_length=255),
        ),
    ]