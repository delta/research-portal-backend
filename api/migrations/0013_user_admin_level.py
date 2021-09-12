# Generated by Django 3.2.4 on 2021-09-12 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20210908_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='admin_level',
            field=models.CharField(choices=[('Normal', 'Normal'), ('Department', 'Department'), ('Global', 'Global')], default='Normal', max_length=25),
        ),
    ]
