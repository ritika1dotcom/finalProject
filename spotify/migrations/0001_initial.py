# Generated by Django 4.2.7 on 2023-11-30 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uri', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('artist_name', models.CharField(max_length=255)),
                ('album_name', models.CharField(max_length=255)),
                ('album_image', models.URLField()),
                ('preview_url', models.URLField(blank=True, null=True)),
            ],
        ),
    ]
