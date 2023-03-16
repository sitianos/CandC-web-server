# Generated by Django 4.1 on 2022-08-26 13:32

import candc.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Puppet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(default='', max_length=30, unique=True)),
                ('username', models.CharField(max_length=30)),
                ('cmd', models.TextField(blank=True, default='')),
                ('upload_file', models.FileField(blank=True, upload_to=candc.models.directory_path)),
                ('last_access', models.DateTimeField()),
            ],
        ),
    ]
