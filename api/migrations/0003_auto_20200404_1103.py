# Generated by Django 3.0.4 on 2020-04-04 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_delete_album'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermeta',
            name='is_private',
            field=models.BooleanField(default=True),
        ),
    ]