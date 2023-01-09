# Generated by Django 3.2.2 on 2023-03-16 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_userinbox'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='dimensions',
        ),
        migrations.AddField(
            model_name='product',
            name='breadth',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='dimension_measurement',
            field=models.CharField(choices=[('cmxcmxcm', 'cmxcmxcm'), ('mmxmmxmm', 'mmxmmxmm')], max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='height',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='length',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='panel_type',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='warranty',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]