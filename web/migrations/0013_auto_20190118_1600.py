# Generated by Django 2.1.5 on 2019-01-18 16:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0012_auto_20190116_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='getpetrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='get_pet_requests', to=settings.AUTH_USER_MODEL, verbose_name='Vartotojas'),
        ),
        migrations.AlterField(
            model_name='userpetchoice',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_pet_choices', to=settings.AUTH_USER_MODEL, verbose_name='Vartotojas'),
        ),
    ]