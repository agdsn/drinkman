# Generated by Django 4.0.3 on 2022-08-30 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drinkman', '0011_transaction_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_guest',
            field=models.BooleanField(default=0),
        ),
    ]