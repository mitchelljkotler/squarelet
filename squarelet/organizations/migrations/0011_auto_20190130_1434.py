# Generated by Django 2.0.6 on 2019-01-30 14:34

# Django
from django.db import migrations, models

# Third Party
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [("organizations", "0010_auto_20181106_2003")]

    operations = [
        migrations.AddField(
            model_name="organization",
            name="avatar",
            field=sorl.thumbnail.fields.ImageField(
                blank=True, upload_to="org_avatars", verbose_name="avatar"
            ),
        )
    ]