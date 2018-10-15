
# Django
from django.core.management.base import BaseCommand
from django.db import transaction

# Standard Library
import csv

# Squarelet
from squarelet.organizations.models import Membership, Organization
from squarelet.users.models import User


class Command(BaseCommand):
    """Import users and orgs from MuckRock"""

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self.import_users()
            self.import_orgs()
            self.import_members()

    def import_users(self):
        with open("users.csv", newline="") as infile:
            reader = csv.reader(infile)
            next(reader)  # discard headers
            for user in reader:
                # XXX skip non unique emails
                if User.objects.filter(email=user[2]).exists():
                    continue
                User.objects.create(
                    id=user[0],
                    username=user[1],
                    email=user[2],
                    password=user[3],
                    name=user[4],
                    is_staff=user[5] == "True",
                    is_active=user[6] == "True",
                    is_superuser=user[7] == "True",
                )

    def import_orgs(self):
        with open("orgs.csv", newline="") as infile:
            reader = csv.reader(infile)
            next(reader)  # discard headers
            for org in reader:
                Organization.objects.create(
                    id=org[0],
                    name=org[1],
                    org_type=int(org[2]),
                    next_org_type=int(org[2]),
                    individual=org[3] == "True",
                    private=org[4] == "True",
                    customer_id=org[5],
                    subscription_id=org[6],
                    date_update=org[7],
                    monthly_requests=int(org[8]),
                    max_users=int(org[9]),
                    monthly_cost=int(org[10]),
                    requests_per_month=int(org[11]),
                )

    def import_members(self):
        with open("members.csv", newline="") as infile:
            reader = csv.reader(infile)
            next(reader)  # discard headers
            for member in reader:
                # XXX skip users we skipped above
                if not User.objects.filter(id=member[0]).exists():
                    continue
                Membership.objects.create(
                    user_id=member[0],
                    organization_id=member[1],
                    admin=member[4] == "True",
                )
