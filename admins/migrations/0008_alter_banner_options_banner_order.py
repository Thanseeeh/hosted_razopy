# Generated by Django 4.1.8 on 2023-05-02 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0007_banner'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='banner',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='banner',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
