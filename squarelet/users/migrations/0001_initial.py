# Generated by Django 2.1.7 on 2019-03-21 15:16

import django.contrib.postgres.fields.citext
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import sorl.thumbnail.fields
import squarelet.core.fields
import squarelet.core.mixins
import squarelet.users.managers
import squarelet.users.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organizations', '0001_initial'),
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('name', models.CharField(max_length=255, verbose_name='name of user')),
                ('email', django.contrib.postgres.fields.citext.CIEmailField(max_length=254, null=True, unique=True, verbose_name='email')),
                ('username', django.contrib.postgres.fields.citext.CICharField(error_messages={'unqiue': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and ./-/_ only.  May only be changed once.', max_length=150, unique=True, validators=[squarelet.users.validators.UsernameValidator()], verbose_name='username')),
                ('avatar', sorl.thumbnail.fields.ImageField(blank=True, max_length=255, upload_to='avatars', verbose_name='avatar')),
                ('can_change_username', models.BooleanField(default=True, help_text='Keeps track of whether or not the user has used their one username change', verbose_name='can change username')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('is_agency', models.BooleanField(default=False, help_text='This is an account used for allowing agencies to log in to the site', verbose_name='agency user')),
                ('source', models.CharField(choices=[('muckrock', 'MuckRock'), ('documentcloud', 'DocumentCloud'), ('foiamachine', 'FOIA Machine'), ('quackbot', 'QuackBot'), ('squarelet', 'Squarelet')], default='squarelet', max_length=11)),
                ('email_failed', models.BooleanField(default=False, help_text="Has an email we sent to this user's email address failed?", verbose_name='email failed')),
                ('created_at', squarelet.core.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created at')),
                ('updated_at', squarelet.core.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='updated at')),
                ('use_autologin', models.BooleanField(default=True, help_text='Links you receive in emails from us will contain a token to automatically log you in', verbose_name='use autologin')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('individual_organization', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.PROTECT, to='organizations.Organization', to_field='uuid')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            bases=(squarelet.core.mixins.AvatarMixin, models.Model),
            managers=[
                ('objects', squarelet.users.managers.UserManager()),
            ],
        ),
    ]
