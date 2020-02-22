# Generated by Django 3.0.3 on 2020-02-22 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_signup', '0005_auto_20200222_2035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_data',
            name='dietary_restrictions',
            field=models.ManyToManyField(choices=[('Vegetarian', 'Vegetarian'), ('Vegan', 'Vegan'), ('None', 'None')], to='user_signup.User_Diet'),
        ),
    ]
