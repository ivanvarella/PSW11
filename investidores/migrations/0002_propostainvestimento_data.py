# Generated by Django 5.0.6 on 2024-08-17 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investidores', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='propostainvestimento',
            name='data',
            field=models.DateTimeField(auto_now_add=True, default='2024-08-01T12:00:00'),
            preserve_default=False,
        ),
    ]