# Generated by Django 2.1.2 on 2019-01-09 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0010_auto_20181120_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpetchoice',
            name='pet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_pet_choices', to='web.Pet', verbose_name='Gyvūnas'),
        ),
    ]