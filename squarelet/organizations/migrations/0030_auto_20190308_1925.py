# Generated by Django 2.1.7 on 2019-03-08 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0029_auto_20190306_1706'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='monthly_cost',
        ),
        migrations.AddField(
            model_name='charge',
            name='fee_amount',
            field=models.PositiveSmallIntegerField(default=0, help_text='Fee percantage', verbose_name='fee amount'),
        ),
    ]