# Generated by Django 3.0.4 on 2020-04-30 22:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0010_pet_information_for_getpet_team'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pet',
            name='cat_friendly',
        ),
        migrations.RemoveField(
            model_name='pet',
            name='child_friendly',
        ),
        migrations.RemoveField(
            model_name='pet',
            name='dog_friendly',
        ),
        migrations.RemoveField(
            model_name='pet',
            name='is_special_care_needed',
        ),
    ]