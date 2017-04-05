# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-14 16:27
from __future__ import unicode_literals

from datetime import datetime, timedelta, date

from django.conf import settings
from django.db import migrations, models
from django.utils import timezone
import django.db.models.deletion

def update_created_ts(subscription, created_date):
    tz = timezone.get_current_timezone()
    new_created = datetime.combine(created_date, datetime.min.time())
    subscription.created_ts = timezone.make_aware(new_created, tz)
    subscription.save()

def forward(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    OldMembership = apps.get_model("nadine", "OldMembership")
    MembershipPlan = apps.get_model("nadine", "MembershipPlan")
    Membership = apps.get_model("nadine", "Membership")
    IndividualMembership = apps.get_model("nadine", "IndividualMembership")
    MembershipPackage = apps.get_model("nadine", "MembershipPackage")
    SubscriptionDefault = apps.get_model("nadine", "SubscriptionDefault")
    ResourceSubscription = apps.get_model("nadine", "ResourceSubscription")
    Resource = apps.get_model("nadine", "Resource")
    print

    print("    Creating Resources...")
    DAY = Resource.objects.create(name="Coworking Day", key="day", tracker_class="nadine.models.resource.CoworkingDayTracker" )
    ROOM = Resource.objects.create(name="Room Booking", key="room", tracker_class="nadine.models.resource.RoomBookingTracker" )
    DESK = Resource.objects.create(name="Dedicated Desk", key="desk")
    MAIL = Resource.objects.create(name="Mail Service", key="mail")
    KEY = Resource.objects.create(name="Key", key="key")

    print("    Migrating Membership Plans to Packages...")
    PACKAGE_MAP = {}
    for plan in MembershipPlan.objects.all():
        package = MembershipPackage.objects.create(name=plan.name, enabled=plan.enabled)
        SubscriptionDefault.objects.create(
            package = package,
            resource = DAY,
            allowance = plan.dropin_allowance,
            monthly_rate = plan.monthly_rate,
            overage_rate=plan.daily_rate
        )
        if plan.has_desk:
            SubscriptionDefault.objects.create(
                package = package,
                resource = DESK,
                allowance = 1,
                monthly_rate = 0,
                overage_rate = 0
            )
        PACKAGE_MAP[plan] = package

    print("    Migrating Memberships...")
    for user in User.objects.all().order_by('id'):
        new_membership = IndividualMembership.objects.create(user = user)
        old_memberships = OldMembership.objects.filter(user=user).order_by('start_date')
        if old_memberships:
            # Set the bill_day and package based on the last membership found
            last_membership = old_memberships.last()
            last_package = PACKAGE_MAP[last_membership.membership_plan]
            new_membership.bill_day = last_membership.start_date.day
            new_membership.package = last_package
            new_membership.save()

            for m in old_memberships:
                # Create a link from the old to the new
                m.new_membership = new_membership
                m.save()

                # Create ResourceSubscriptions based on the parameters of the old membership
                if m.has_desk:
                    s = ResourceSubscription.objects.create(
                        membership = new_membership,
                        resource = DESK,
                        start_date = m.start_date,
                        end_date = m.end_date,
                        monthly_rate = m.monthly_rate,
                        allowance = 1,
                        overage_rate = 0,
                        paid_by = m.paid_by,
                    )
                    update_created_ts(s, m.start_date)
                    s = ResourceSubscription.objects.create(
                        membership = new_membership,
                        resource = DAY,
                        start_date = m.start_date,
                        end_date = m.end_date,
                        monthly_rate = 0,
                        allowance = m.dropin_allowance,
                        overage_rate = m.daily_rate,
                        paid_by = m.paid_by,
                    )
                    update_created_ts(s, m.start_date)
                else:
                    s = ResourceSubscription.objects.create(
                        membership = new_membership,
                        resource = DAY,
                        start_date = m.start_date,
                        end_date = m.end_date,
                        monthly_rate = m.monthly_rate,
                        allowance = m.dropin_allowance,
                        overage_rate = m.daily_rate,
                        paid_by = m.paid_by,
                    )
                    update_created_ts(s, m.start_date)
                if m.has_mail:
                    s = ResourceSubscription.objects.create(
                        membership = new_membership,
                        resource = MAIL,
                        start_date = m.start_date,
                        end_date = m.end_date,
                        monthly_rate = 0,
                        allowance = 1,
                        overage_rate = 0,
                        paid_by = m.paid_by,
                    )
                    update_created_ts(s, m.start_date)
                if m.has_key:
                    s = ResourceSubscription.objects.create(
                        membership = new_membership,
                        resource = KEY,
                        start_date = m.start_date,
                        end_date = m.end_date,
                        monthly_rate = 0,
                        allowance = 1,
                        overage_rate = 0,
                        paid_by = m.paid_by,
                    )
                    update_created_ts(s, m.start_date)


def reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nadine', '0027_old_models'),
    ]

    operations = [

        migrations.CreateModel(
            name='MembershipPackage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill_day', models.SmallIntegerField(default=1)),
                ('package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nadine.MembershipPackage')),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('key', models.CharField(max_length=8, blank=True, null=True)),
                ('tracker_class', models.CharField(max_length=64, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionDefault',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allowance', models.IntegerField(default=0)),
                ('monthly_rate', models.DecimalField(decimal_places=2, max_digits=9)),
                ('overage_rate', models.DecimalField(decimal_places=2, max_digits=9)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='defaults', to='nadine.MembershipPackage')),
                ('resource', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='nadine.Resource')),
            ],
        ),
        migrations.CreateModel(
            name='IndividualMembership',
            fields=[
                ('membership_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='nadine.Membership')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='membership', to=settings.AUTH_USER_MODEL)),
            ],
            bases=('nadine.membership',),
        ),
        migrations.CreateModel(
            name='OrganizationMembership',
            fields=[
                ('membership_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='nadine.Membership')),
                ('organization', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='membership', to='nadine.Organization')),
            ],
            bases=('nadine.membership',),
        ),
        migrations.CreateModel(
            name='ResourceSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_ts', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('description', models.CharField(blank=True, max_length=64, null=True)),
                ('allowance', models.IntegerField(default=0)),
                ('start_date', models.DateField(db_index=True)),
                ('end_date', models.DateField(blank=True, db_index=True, null=True)),
                ('monthly_rate', models.DecimalField(decimal_places=2, max_digits=9)),
                ('overage_rate', models.DecimalField(decimal_places=2, max_digits=9)),
            ],
        ),
        migrations.AddField(
            model_name='resourcesubscription',
            name='membership',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='nadine.Membership'),
        ),
        migrations.AddField(
            model_name='resourcesubscription',
            name='paid_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='resourcesubscription',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nadine.Resource'),
        ),
        migrations.AddField(
            model_name='membershippackage',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='oldmembership',
            name='new_membership',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='nadine.Membership'),
        ),

        # Convert all the old memberships to new ones
        migrations.RunPython(forward, reverse),

    ]
