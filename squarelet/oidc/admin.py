# Django
from django.contrib import admin

# Third Party
from oidc_provider.admin import ClientAdmin
from oidc_provider.models import Client
from reversion.admin import VersionAdmin

# Squarelet
from squarelet.oidc.models import ClientProfile

admin.site.unregister(Client)


class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    extra = 0
    max_number = 1


@admin.register(Client)
class MyClientAdmin(VersionAdmin, ClientAdmin):
    inlines = [ClientProfileInline]
