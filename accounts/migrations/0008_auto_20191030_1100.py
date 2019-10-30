# Generated by Django 2.2.6 on 2019-10-30 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20191029_1933'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='from_account',
        ),
        migrations.RemoveField(
            model_name='request',
            name='user',
        ),
        migrations.RemoveField(
            model_name='account',
            name='owner_type',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='status',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user_money',
        ),
        migrations.AddField(
            model_name='transaction',
            name='limit',
            field=models.IntegerField(default=15),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='ttype',
            field=models.CharField(blank=True, choices=[('T', 'Transfer')], editable=False, max_length=2),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('C', 'Casual'), ('P', 'Premium'), ('V', 'Commercial')], max_length=1),
        ),
        migrations.DeleteModel(
            name='Article',
        ),
        migrations.DeleteModel(
            name='Request',
        ),
    ]