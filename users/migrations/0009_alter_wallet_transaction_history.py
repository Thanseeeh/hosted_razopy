# Generated by Django 4.1.8 on 2023-04-24 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_wallet_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='transaction_history',
            field=models.JSONField(default=list),
        ),
    ]
