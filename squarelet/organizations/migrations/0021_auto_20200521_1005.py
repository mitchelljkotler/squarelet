# Generated by Django 2.1.7 on 2020-05-21 14:05

# Django
from django.db import migrations


def delete_free_plan(apps, schema_editor):
    Plan = apps.get_model("organizations", "Plan")
    Organization = apps.get_model("organizations", "Organization")
    OrganizationChangeLog = apps.get_model("organizations", "OrganizationChangeLog")
    try:
        free_plan = Plan.objects.get(slug="free")
        Organization.objects.filter(_plan=free_plan).update(_plan=None)
        Organization.objects.filter(next_plan=free_plan).update(next_plan=None)
        OrganizationChangeLog.objects.filter(from_plan=free_plan).update(from_plan=None)
        OrganizationChangeLog.objects.filter(to_plan=free_plan).update(to_plan=None)
        OrganizationChangeLog.objects.filter(from_next_plan=free_plan).update(
            from_next_plan=None
        )
        OrganizationChangeLog.objects.filter(to_next_plan=free_plan).update(
            to_next_plan=None
        )
        free_plan.delete()
    except Plan.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [("organizations", "0020_auto_20200516_1123")]

    operations = [migrations.RunPython(delete_free_plan, migrations.RunPython.noop)]