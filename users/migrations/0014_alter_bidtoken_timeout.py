# Generated by Django 4.1.8 on 2023-05-11 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_bidtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bidtoken',
            name='timeout',
            field=models.DateTimeField(null=True),
        ),
    ]
