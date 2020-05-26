# Generated by Django 2.1.7 on 2020-05-26 20:16

# Django
from django.db import migrations

# Third Party
from autoslug.settings import slugify


def redo_slugs(apps, schema_editor):
    """Set resources for MuckRock entitlements"""
    Entitlement = apps.get_model("organizations", "Entitlement")
    for entitlement in Entitlement.objects.all():
        entitlement.slug = slugify(entitlement.name)
        entitlement.save()


def redo_proxy(apps, schema_editor):
    Entitlement = apps.get_model("organizations", "Entitlement")
    Plan = apps.get_model("organizations", "Plan")
    Client = apps.get_model("oidc_provider", "Client")

    muckrock_client, _created = Client.objects.get_or_create(
        name__startswith="MuckRock", defaults={"name": "MuckRock"}
    )
    proxy_entitlement = Entitlement.objects.create(
        name="Proxy",
        description="Marks an individual as a proxy user, as well as giving them "
        "the equivalent resources as a Professional user",
        client=muckrock_client,
        resources={
            "minimum_users": 1,
            "base_requests": 20,
            "requests_per_user": 0,
            "feature_level": 1,
            "proxy": True,
        },
    )
    proxy_plan = Plan.objects.get(name="Proxy")
    proxy_plan.entitlements.set([proxy_entitlement])


class Migration(migrations.Migration):

    dependencies = [("organizations", "0022_auto_20200526_1556")]

    operations = [
        migrations.RunPython(redo_slugs, migrations.RunPython.noop),
        migrations.RunPython(redo_proxy, migrations.RunPython.noop),
    ]