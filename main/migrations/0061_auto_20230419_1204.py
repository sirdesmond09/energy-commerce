# Generated by Django 3.2.2 on 2023-04-19 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0060_alter_frequentlyaskedquestion_answer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supportticket',
            name='user',
        ),
        migrations.AddField(
            model_name='supportticket',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='supportticket',
            name='first_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='supportticket',
            name='last_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='supportticket',
            name='phone',
            field=models.CharField(max_length=255, null=True),
        ),
    ]