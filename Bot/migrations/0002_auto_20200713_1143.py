# Generated by Django 3.0.8 on 2020-07-13 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='lastname',
            field=models.CharField(max_length=199, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='username',
            field=models.CharField(max_length=199, null=True),
        ),
    ]
