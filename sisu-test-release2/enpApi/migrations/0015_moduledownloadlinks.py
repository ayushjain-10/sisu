# Generated by Django 2.0.5 on 2021-04-23 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enpApi', '0014_player_registration_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleDownloadLinks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('training_type', models.CharField(choices=[('Desktop', 'Desktop'), ('VR', 'VR')], max_length=255)),
                ('category', models.CharField(choices=[('None', 'None'), ('Harassment Training', 'Harassment Training')], max_length=255)),
                ('download_link', models.CharField(max_length=554)),
                ('is_supervisor', models.BooleanField()),
            ],
        ),
    ]