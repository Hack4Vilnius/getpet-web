# Generated by Django 3.0.7 on 2020-06-08 09:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('web', '0038_auto_20200606_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='full_name',
            field=models.CharField(default='default', help_text='Pavyzdžiui: Vilniaus regionas', max_length=100,
                                   verbose_name='Pilnas regiono pavadinimas'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='region',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Regiono pavadinimas'),
        ),
    ]
