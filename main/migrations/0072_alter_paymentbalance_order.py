# Generated by Django 4.1 on 2023-07-14 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0071_rename_spectaid_paymentbalance_spectaid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentbalance',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.order'),
        ),
    ]
