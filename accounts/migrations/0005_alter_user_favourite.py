# Generated by Django 3.2.2 on 2023-02-23 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20230223_1153'),
        ('accounts', '0004_auto_20230223_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='favourite',
            field=models.ManyToManyField(blank=True, to='main.Product'),
        ),
    ]