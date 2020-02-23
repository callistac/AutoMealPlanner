# Generated by Django 3.0.3 on 2020-02-23 16:16

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User_Diet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dietary_restrictions', multiselectfield.db.fields.MultiSelectField(choices=[('Vegetarian', 'Vegetarian'), ('Vegan', 'Vegan')], max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='User_Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(default='', max_length=500)),
                ('lastname', models.CharField(default='', max_length=500)),
                ('email', models.EmailField(default='', max_length=500)),
                ('zip', models.PositiveIntegerField()),
                ('budget', models.CharField(choices=[('<$40', '<$40'), ('$40-60', '$40-60'), ('$60-80', '$60-80'), ('$80-100', '$80-100'), ('>$100', '>$100')], default='', max_length=500)),
                ('laziness', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], default='', max_length=50)),
                ('dietary_restrictions', models.ManyToManyField(choices=[('Vegetarian', 'Vegetarian'), ('Vegan', 'Vegan'), ('Peanut', 'Peanut')], default='', to='user_signup.User_Diet')),
            ],
        ),
    ]
