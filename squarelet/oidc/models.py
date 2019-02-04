"""Models for the OIDC app"""

# Django
from django.db import models

# Standard Library
import hashlib
import hmac
import time

# Third Party
import requests


class ClientProfile(models.Model):
    """Extra information for OIDC clients"""

    client = models.OneToOneField("oidc_provider.Client", on_delete=models.CASCADE)
    webhook_url = models.URLField(blank=True)

    def __str__(self):
        return str(self.client)

    def send_cache_invalidation(self, model, uuids):
        """Send a cache invalidation to this client"""
        timestamp = int(time.time())
        signature = hmac.new(
            key=self.client.client_secret.encode("utf8"),
            msg="{}{}{}".format(timestamp, model, "".join(uuids)).encode("utf8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        data = {
            "type": model,
            "uuids": uuids,
            "timestamp": timestamp,
            "signature": signature,
        }
        requests.post(self.webhook_url, data=data)
