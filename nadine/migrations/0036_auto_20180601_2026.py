# Generated by Django 2.0.3 on 2018-06-01 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nadine', '0035_auto_20180413_2326'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbill',
            name='cached_total_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='userbill',
            name='cached_total_owed',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='userbill',
            name='cached_total_paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
        migrations.AddField(
            model_name='userbill',
            name='cached_total_tax_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
    ]