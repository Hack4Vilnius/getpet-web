# Generated by Django 3.0.7 on 2020-06-06 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0037_auto_20200606_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shelter',
            name='address',
            field=models.CharField(max_length=256, verbose_name='Prieglaudos adresas'),
        ),
        migrations.AlterField(
            model_name='shelter',
            name='latitude',
            field=models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Vietos platuma'),
        ),
        migrations.AlterField(
            model_name='shelter',
            name='longitude',
            field=models.DecimalField(decimal_places=6, max_digits=9, verbose_name='Vietos ilguma'),
        ),
    ]