# Django
from celery.task import task

# Local
from .models import ClientProfile


@task(name="squarelet.oidc.tasks.send_cache_invalidation")
def send_cache_invalidation(client_profile_pk, model, uuids):
    client_profile = ClientProfile.objects.get(pk=client_profile_pk)
    client_profile.send_cache_invalidation(model, uuids)
