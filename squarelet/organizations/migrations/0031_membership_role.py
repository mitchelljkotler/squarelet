# Generated by Django 2.1.7 on 2019-03-13 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0030_auto_20190308_1925'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='role',
            field=models.IntegerField(choices=[(0, 'Disabled'), (1, 'Administrator'), (2, 'Contributor'), (3, 'Reviewer'), (4, 'Freelancer')], default=1),
            preserve_default=False,
        ),
    ]
