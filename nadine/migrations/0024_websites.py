# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-07 17:49


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def forward(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    Organization = apps.get_model("nadine", "Organization")
    Website = apps.get_model("nadine", "Website")
    URL = apps.get_model("nadine", "URL")

    for user in User.objects.all():
        for u in user.url_set.all():
            user.profile.websites.create(url_type = u.url_type, url=u.url_value)


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('nadine', '0023_auto_20161122_1315'),
    ]

    operations = [
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(blank=True, null=True)),
                ('url_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nadine.URLType')),
            ],
        ),
        migrations.AddField(
            model_name='userprofile',
            name='websites',
            field=models.ManyToManyField(blank=True, to='nadine.Website'),
        ),
        migrations.AddField(
            model_name='organization',
            name='websites',
            field=models.ManyToManyField(blank=True, to='nadine.Website'),
        ),
        migrations.RunPython(forward, reverse),
        migrations.RemoveField(
            model_name='url',
            name='url_type',
        ),
        migrations.RemoveField(
            model_name='url',
            name='user',
        ),
        migrations.DeleteModel(
            name='URL',
        ),
    ]
