# Generated by Django 4.1.2 on 2023-01-12 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qalib', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qalibquestion',
            name='tags',
            field=models.ManyToManyField(blank=True, to='qalib.qalibtag'),
        ),
    ]
