# Generated by Django 2.2.6 on 2019-10-29 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20191028_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='privatekey',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='secretkey',
            field=models.TextField(blank=True),
        ),
    ]