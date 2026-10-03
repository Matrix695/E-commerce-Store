from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import CustomerProfile


class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={"autocomplete": "name"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    address = forms.CharField(max_length=220, widget=forms.TextInput(attrs={"autocomplete": "street-address"}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"autocomplete": "address-level2"}))
    postal_code = forms.CharField(max_length=20, label="ZIP / postal code", widget=forms.TextInput(attrs={"autocomplete": "postal-code"}))


class UserRegistrationForm(UserCreationForm):
    field_order = ("username", "email", "contact_number", "password1", "password2")

    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    contact_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email


class CustomerAuthenticationForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": _("Please enter a correct email address or contact number and password."),
    }
    username = forms.CharField(
        label="Email or contact number",
        widget=forms.TextInput(attrs={"autocomplete": "username", "autofocus": True}),
    )

    def clean(self):
        identifier = self.cleaned_data.get("username", "").strip()
        password = self.cleaned_data.get("password")
        if identifier and password:
            if "@" in identifier:
                matching_users = User.objects.filter(email__iexact=identifier)
                user = matching_users.first() if matching_users.count() == 1 else None
            else:
                matching_profiles = CustomerProfile.objects.select_related("user").filter(
                    contact_number=identifier,
                )
                profile = matching_profiles.first() if matching_profiles.count() == 1 else None
                user = profile.user if profile else None
            self.cleaned_data["username"] = user.get_username() if user else "__invalid_login_identifier__"
        return super().clean()
