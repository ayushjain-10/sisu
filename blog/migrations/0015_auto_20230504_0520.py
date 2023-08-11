# Generated by Django 2.0.5 on 2023-05-04 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0014_alter_mediumpost_m_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Press_aj',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_m2', models.CharField(max_length=250)),
                ('Summary_m2', models.CharField(max_length=374)),
                ('pub_date_m2', models.DateTimeField(null=True, verbose_name='date published')),
                ('title_m', models.CharField(max_length=100)),
                ('m_photo', models.ImageField(null=True, upload_to='medium/photos')),
            ],
        ),
        migrations.AlterField(
            model_name='mediumpost',
            name='m_photo',
            field=models.ImageField(null=True, upload_to='medium/photos'),
        ),
    ]