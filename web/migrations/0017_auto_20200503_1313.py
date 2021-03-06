# Generated by Django 3.0.5 on 2020-05-03 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0016_remove_pet_is_vaccinated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pet',
            name='age',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Amžius'),
        ),
        migrations.AlterField(
            model_name='pet',
            name='desexed',
            field=models.BooleanField(choices=[(True, 'Taip'), (False, 'Ne'), (None, 'Nepatikslinta')], null=True, verbose_name='Kastruotas / sterilizuotas'),
        ),
        migrations.AlterField(
            model_name='pet',
            name='weight',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Svoris'),
        ),
    ]
