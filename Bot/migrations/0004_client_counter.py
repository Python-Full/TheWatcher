# Generated by Django 3.0.8 on 2020-07-14 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Bot', '0003_site_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='counter',
            field=models.IntegerField(default=1),
        ),
    ]
