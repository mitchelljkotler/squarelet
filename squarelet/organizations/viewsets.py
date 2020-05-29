# Third Party
import django_filters
from rest_framework import mixins, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoObjectPermissions, IsAdminUser

# Squarelet
from squarelet.core.permissions import DjangoObjectPermissionsOrAnonReadOnly
from squarelet.oidc.permissions import ScopePermission
from squarelet.organizations.choices import ChangeLogReason, StripeAccounts
from squarelet.organizations.models import (
    Charge,
    Entitlement,
    Invitation,
    Membership,
    Organization,
    Plan,
    Subscription,
)
from squarelet.organizations.serializers import (
    ChargeSerializer,
    OrganizationSerializer,
    PressPassEntitlmentSerializer,
    PressPassInvitationSerializer,
    PressPassMembershipSerializer,
    PressPassNestedInvitationSerializer,
    PressPassOrganizationSerializer,
    PressPassPlanSerializer,
    PressPassSubscriptionSerializer,
    PressPassUserInvitationsSerializer,
    PressPassUserMembershipsSerializer,
)
from squarelet.users.models import User


class OrganizationViewSet(viewsets.ModelViewSet):
    # remove _plan after clients are updated
    queryset = Organization.objects.select_related("_plan")
    serializer_class = OrganizationSerializer
    permission_classes = (ScopePermission | IsAdminUser,)
    read_scopes = ("read_organization",)
    write_scopes = ("write_organization",)
    lookup_field = "uuid"
    swagger_schema = None


class ChargeViewSet(viewsets.ModelViewSet):
    queryset = Charge.objects.all()
    serializer_class = ChargeSerializer
    permission_classes = (ScopePermission | IsAdminUser,)
    read_scopes = ("read_charge",)
    write_scopes = ("write_charge",)
    swagger_schema = None


class PressPassOrganizationViewSet(
    # Cannot destroy organizations
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Organization.objects.none()
    serializer_class = PressPassOrganizationSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly,)
    lookup_field = "uuid"

    def get_queryset(self):
        return Organization.objects.get_viewable(self.request.user)

    def perform_create(self, serializer):
        organization = serializer.save()
        organization.add_creator(self.request.user)
        organization.change_logs.create(
            reason=ChangeLogReason.created,
            user=self.request.user,
            to_plan=organization.plan,
            to_max_users=organization.max_users,
        )

    def perform_update(self, serializer):
        """Update the subscription on stripe if max users changes"""
        update_subscriptions = (
            serializer.validated_data.get("max_users") != serializer.instance.max_users
        )
        super().perform_update(serializer)
        if update_subscriptions:
            for subscription in serializer.instance.subscriptions.all():
                subscription.stripe_modify()

    class Filter(django_filters.FilterSet):
        user = django_filters.ModelChoiceFilter(
            queryset=User.objects.all(), to_field_name="uuid", field_name="users"
        )

        class Meta:
            model = Organization
            fields = ["user"]

    filterset_class = Filter


class PressPassMembershipViewSet(
    # Cannot create memberships directly - must use invitations
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Membership.objects.none()
    serializer_class = PressPassMembershipSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly,)
    lookup_field = "user__uuid"

    def get_queryset(self):
        """Only fetch both organizations and memberships viewable to this user"""
        organization = get_object_or_404(
            Organization.objects.get_viewable(self.request.user),
            uuid=self.kwargs["organization_uuid"],
        )
        return organization.memberships.all()


class PressPassNestedInvitationViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    The nested invitation view set is for requesting to join an organization,
    inviting somebody to join your organization and seeing who has requested to join
    your organization
    """

    queryset = Invitation.objects.none()
    serializer_class = PressPassNestedInvitationSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly,)

    def get_queryset(self):
        """Only fetch both organizations and inivtations viewable to this user"""
        organization = get_object_or_404(
            Organization.objects.get_viewable(self.request.user),
            uuid=self.kwargs["organization_uuid"],
        )
        if organization.has_admin(self.request.user):
            return organization.invitations.all()
        else:
            return organization.invitations.none()

    def perform_create(self, serializer):
        organization = get_object_or_404(
            Organization.objects.get_viewable(self.request.user),
            uuid=self.kwargs["organization_uuid"],
        )
        # Admins will set an email address to invite
        if organization.has_admin(self.request.user):
            invitation = serializer.save(organization=organization, request=False)
        # Users can also request to join - no email address is used, we set
        # `user` to the current user
        else:
            invitation = serializer.save(
                organization=organization, request=True, user=self.request.user
            )
        invitation.send(source="presspass")


class PressPassInvitationViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """
    The stand alone invitation viewset is for viewing and accepting or rejecting
    your invitations
    """

    queryset = Invitation.objects.all()
    serializer_class = PressPassInvitationSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly,)
    lookup_field = "uuid"

    def perform_update(self, serializer):
        """Accept or reject the invitation"""
        if serializer.validated_data.get("accept"):
            serializer.instance.accept(self.request.user)
        elif serializer.validated_data.get("reject"):
            serializer.instance.reject()


def plan_filter_organizations(request):
    if request is None or not request.user.is_authenticated:
        return Organization.objects.none()
    else:
        return request.user.organizations.all()


class PressPassPlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.none()
    serializer_class = PressPassPlanSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly,)

    def get_queryset(self):
        return Plan.objects.get_viewable(self.request.user)

    class Filter(django_filters.FilterSet):
        organization = django_filters.ModelChoiceFilter(
            queryset=plan_filter_organizations,
            method="organization_choices",
            to_field_name="uuid",
        )
        account = django_filters.ChoiceFilter(
            choices=StripeAccounts.choices, field_name="stripe_account"
        )

        def organization_choices(self, queryset, _name, value):
            return queryset.choices(value)

        class Meta:
            model = Plan
            fields = ["organization", "account"]

    filterset_class = Filter


class PressPassUserInvitationViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Invitation.objects.none()
    serializer_class = PressPassUserInvitationsSerializer
    permission_classes = (DjangoObjectPermissions,)
    lookup_field = "user__uuid"

    def get_queryset(self):
        user = self.request.user

        if self.kwargs["user_uuid"] == "me" or self.kwargs["user_uuid"] == str(
            user.uuid
        ):
            return user.invitations.all()
        else:
            return self.queryset


class PressPassUserMembershipViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Membership.objects.none()
    serializer_class = PressPassUserMembershipsSerializer
    permission_classes = (DjangoObjectPermissions,)
    lookup_field = "user__uuid"

    def get_queryset(self):
        user = self.request.user

        if self.kwargs["user_uuid"] == "me" or self.kwargs["user_uuid"] == str(
            user.uuid
        ):
            return user.memberships.get_viewable(user)
        else:
            return self.queryset


class PressPassEntitlementViewSet(viewsets.ModelViewSet):
    queryset = Entitlement.objects.none()
    serializer_class = PressPassEntitlmentSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly,)

    def get_queryset(self):
        queryset = self.queryset

        if self.request.query_params.get("subscribed"):
            queryset = queryset | Entitlement.objects.get_subscribed(self.request.user)

        if self.request.query_params.get("owned"):
            queryset = queryset | Entitlement.objects.get_owned(self.request.user)

        if not self.request.query_params.get(
            "subscribed"
        ) and not self.request.query_params.get("owned"):
            queryset = queryset | Entitlement.objects.get_viewable(self.request.user)

        return queryset


class PressPassSubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Subscription.objects.none()
    serializer_class = PressPassSubscriptionSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly,)

    def get_queryset(self):
        """Only fetch both organizations and subscriptions viewable to this user"""
        organization = get_object_or_404(
            Organization.objects.get_viewable(self.request.user),
            uuid=self.kwargs["organization_uuid"],
        )
        if organization.has_admin(self.request.user):
            return organization.subscriptions.all()
        else:
            return organization.subscriptions.none()

    def perform_create(self, serializer):
        organization = get_object_or_404(
            Organization.objects.get_viewable(self.request.user),
            uuid=self.kwargs["organization_uuid"],
        )
        organization.create_subscription(
            serializer.validated_data.get("token"), serializer.validated_data["plan"]
        )

        organization.change_logs.create(
            user=self.request.user,
            reason=ChangeLogReason.updated,
            from_max_users=organization.max_users,
            to_plan=serializer.validated_data["plan"],
            to_max_users=organization.max_users,
        )

    def perform_destroy(self, instance):
        instance.cancel()

        instance.organization.change_logs.create(
            user=self.request.user,
            reason=ChangeLogReason.updated,
            from_plan=instance.plan,
            from_max_users=instance.organization.max_users,
            to_max_users=instance.organization.max_users,
        )
