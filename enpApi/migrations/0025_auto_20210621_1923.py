# Generated by Django 2.0.5 on 2021-06-21 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enpApi', '0024_auto_20210621_1616'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='selectedadjective',
            name='adj_id',
        ),
        migrations.AddField(
            model_name='selectedadjective',
            name='adj_id',
            field=models.ManyToManyField(null=True, to='enpApi.Adjective'),
        ),
    ]
