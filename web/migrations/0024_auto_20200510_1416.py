# Generated by Django 3.0.6 on 2020-05-10 14:16

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0023_auto_20200510_1105'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shelter',
            options={'default_related_name': 'shelters', 'ordering': ['-pk'], 'verbose_name': 'Gyvūnų prieglauda', 'verbose_name_plural': 'Gyvūnų prieglaudos'},
        ),
        migrations.AlterField(
            model_name='shelter',
            name='authenticated_users',
            field=models.ManyToManyField(blank=True, help_text='Priskirti vartotojai gali matyti prieglaudos gyvūnus ir juos tvarkyti.', related_name='shelters', to=settings.AUTH_USER_MODEL, verbose_name='Vartotojai tvarkantys prieglaudos informaciją'),
        ),
    ]
