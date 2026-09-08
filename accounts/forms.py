from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.core.exceptions import ValidationError

from accounts.domains import allowed_domains_for_role, email_domain_allowed
from accounts.models import LecturerProfile, StudentProfile, User


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "autocomplete": "email",
                "class": "input",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "input",
            }
        ),
    )


class PresentPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "input", "autocomplete": "email"}),
    )


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "input", "autocomplete": "given-name"}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "input", "autocomplete": "family-name"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "input", "autocomplete": "email"}),
    )
    student_id = forms.CharField(
        max_length=32,
        required=False,
        label="Student ID",
        widget=forms.TextInput(attrs={"class": "input", "autocomplete": "off"}),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, role=None, **kwargs):
        self.role = role
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["class"] = "input"
        self.fields["password2"].widget.attrs["class"] = "input"
        if role == User.Role.STUDENT:
            self.fields["student_id"].required = True
        domains = ", ".join(f"@{d}" for d in allowed_domains_for_role(role or ""))
        if domains:
            self.fields["email"].help_text = f"Use a university address ({domains})."

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"])
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        if self.role and not email_domain_allowed(email, self.role):
            raise ValidationError(
                "That email domain is not allowed for this account type."
            )
        return email

    def clean_student_id(self):
        student_id = (self.cleaned_data.get("student_id") or "").strip()
        if self.role != User.Role.STUDENT:
            return ""
        if not student_id:
            raise ValidationError("Student ID is required.")
        if StudentProfile.objects.filter(student_id__iexact=student_id).exists():
            raise ValidationError("This student ID is already registered.")
        return student_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.role
        if commit:
            user.save()
            self._create_profile(user)
        return user

    def _create_profile(self, user):
        if user.role == User.Role.STUDENT:
            StudentProfile.objects.create(
                user=user,
                student_id=self.cleaned_data["student_id"],
            )
        elif user.role == User.Role.LECTURER:
            LecturerProfile.objects.create(user=user)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "input", "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"class": "input", "autocomplete": "family-name"}),
            "email": forms.EmailInput(attrs={"class": "input", "autocomplete": "email"}),
        }

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"])
        if not email_domain_allowed(email, self.instance.role):
            raise ValidationError(
                "That email domain is not allowed for this account type."
            )
        exists = (
            User.objects.exclude(pk=self.instance.pk)
            .filter(email__iexact=email)
            .exists()
        )
        if exists:
            raise ValidationError("An account with this email already exists.")
        return email


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ("programme", "level", "department")
        widgets = {
            "programme": forms.TextInput(attrs={"class": "input"}),
            "level": forms.TextInput(attrs={"class": "input"}),
            "department": forms.TextInput(attrs={"class": "input"}),
        }


class LecturerProfileForm(forms.ModelForm):
    class Meta:
        model = LecturerProfile
        fields = ("staff_id", "department")
        widgets = {
            "staff_id": forms.TextInput(attrs={"class": "input"}),
            "department": forms.TextInput(attrs={"class": "input"}),
        }


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"


class StyledSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"
