# Generated by Django 2.0.5 on 2019-06-24 21:09

import blog.models
from django.db import migrations, models
import enumfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20190331_1751'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('category_name', enumfields.fields.EnumField(default='Harassment', enum=blog.models.Category, max_length=30)),
                ('res_url', models.URLField(max_length=250)),
            ],
        ),
    ]