# Generated by Django 3.0.4 on 2020-04-28 19:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_shelter_square_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='petprofilephoto',
            name='pet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_photos', to='web.Pet'),
        ),
    ]
