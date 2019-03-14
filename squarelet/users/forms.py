# Django
# Third Party
import stripe
from allauth.account import forms as allauth
from allauth.account.utils import setup_user_email
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.contrib import messages
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import FormView

# Squarelet
from squarelet.core.forms import StripeForm
from squarelet.core.layout import Field
from squarelet.organizations.models import Organization, Plan
from squarelet.users.models import User


class SignupForm(allauth.SignupForm, StripeForm):
    """Add a name field to the sign up form"""

    name = forms.CharField(
        max_length=255, widget=forms.TextInput(attrs={"placeholder": "Full name"})
    )

    plan = forms.ModelChoiceField(
        label=_("Plan"),
        queryset=Plan.objects.filter(public=True),
        empty_label=None,
        to_field_name="slug",
        widget=forms.HiddenInput(),
    )
    organization_name = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["stripe_token"].required = False

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("stripe_token"),
            Field("stripe_pk"),
            Field("name"),
            Field("username"),
            Field("email", type="email"),
            Field("password1", type="password", css_class="_cls-passwordInput"),
        )
        self.fields["username"].widget.attrs.pop("autofocus", None)
        self.helper.form_tag = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["plan_info"] = {
            p["slug"]: p
            for p in Plan.objects.values(
                "pk", "slug", "base_price", "price_per_user", "minimum_users"
            )
        }
        return context

    def clean(self):
        data = super().clean()
        plan = data["plan"]
        if not plan.free() and not data.get("stripe_token"):
            self.add_error(
                "plan",
                _("You must supply a credit card number to upgrade to a non-free plan"),
            )
        if not plan.for_individuals and not data.get("organization_name"):
            self.add_error(
                "organization_name",
                _(
                    "Organization name is required if registering an "
                    "organizational account"
                ),
            )
        return data

    @transaction.atomic()
    def save(self, request):

        user = User.objects.create_user(
            username=self.cleaned_data.get("username"),
            email=self.cleaned_data.get("email"),
            password=self.cleaned_data.get("password1"),
            name=self.cleaned_data.get("name"),
            source=request.GET.get("intent", "squarelet").lower().strip(),
        )
        setup_user_email(request, user, [])

        free_plan = Plan.objects.get(slug="free")
        plan = self.cleaned_data["plan"]
        try:
            if not plan.free() and plan.for_individuals:
                user.individual_organization.set_subscription(
                    self.cleaned_data.get("stripe_token"), plan, max_users=1
                )

            if not plan.free() and plan.for_groups:
                group_organization = Organization.objects.create(
                    name=self.cleaned_data["organization_name"],
                    plan=free_plan,
                    next_plan=free_plan,
                )
                group_organization.add_creator(user)
                group_organization.set_subscription(
                    self.cleaned_data.get("stripe_token"), plan, max_users=5
                )
        except stripe.error.StripeError as exc:
            messages.error(request, "Payment error: {}".format(exc.user_message))
        return user


class LoginForm(allauth.LoginForm):
    """Customize the login form layout"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("login", css_class="_cls-usernameInput"),
            Field("password", type="password"),
        )
        self.fields["login"].widget.attrs.pop("autofocus", None)
        self.helper.form_tag = False


class AddEmailForm(allauth.AddEmailForm):
    """Customize the add email form layout"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(Field("email", type="email"))
        self.helper.form_tag = False


class ChangePasswordForm(allauth.ChangePasswordForm):
    """Customize the change password form layout"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("oldpassword", type="password", css_class="_cls-passwordInput"),
            Field("password1", type="password", css_class="_cls-passwordInput"),
            Field("password2", type="password", css_class="_cls-passwordInput"),
        )
        self.helper.form_tag = False


class SetPasswordForm(allauth.SetPasswordForm):
    """Customize the set password form layout"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("password1", type="password", css_class="_cls-passwordInput"),
            Field("password2", type="password", css_class="_cls-passwordInput"),
        )
        self.helper.form_tag = False


class ResetPasswordForm(allauth.ResetPasswordForm):
    """Customize the reset password form layout"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(Field("email", type="email"))
        self.helper.form_tag = False


class ResetPasswordKeyForm(allauth.ResetPasswordKeyForm):
    """Customize the reset password key form layout"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("password1", type="password", css_class="_cls-passwordInput"),
            Field("password2", type="password", css_class="_cls-passwordInput"),
        )
        self.helper.form_tag = False
