# Generated by Django 4.1.2 on 2023-04-16 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_resources', '0007_remove_nonexerciselearningresource_related_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='exerciselearningresource',
            name='related_to',
            field=models.ManyToManyField(related_name='related', to='learning_resources.exerciselearningresource'),
        ),
    ]
