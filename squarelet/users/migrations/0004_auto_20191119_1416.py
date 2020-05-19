# Generated by Django 2.1.7 on 2019-11-19 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20191024_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='source',
            field=models.CharField(choices=[('muckrock', 'MuckRock'), ('documentcloud', 'DocumentCloud'), ('foiamachine', 'FOIA Machine'), ('quackbot', 'QuackBot'), ('squarelet', 'Squarelet'), ('presspass', 'PressPass')], default='squarelet', help_text='Which service did this user originally sign up for?', max_length=13, verbose_name='source'),
        ),
    ]
