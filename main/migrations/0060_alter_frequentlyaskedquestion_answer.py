# Generated by Django 3.2.2 on 2023-04-18 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0059_auto_20230417_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frequentlyaskedquestion',
            name='answer',
            field=models.TextField(null=True),
        ),
    ]