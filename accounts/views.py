from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from accounts.forms import (
    EmailAuthenticationForm,
    LecturerProfileForm,
    PresentPasswordResetForm,
    ProfileForm,
    RegistrationForm,
    StudentProfileForm,
    StyledPasswordChangeForm,
    StyledSetPasswordForm,
)
from accounts.mixins import StudentRequiredMixin, redirect_for_role
from accounts.models import LecturerProfile, User
from courses.models import CourseParticipant


class HomeView(TemplateView):
    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect_for_role(request.user)
        return super().get(request, *args, **kwargs)


class PresentLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_lecturer:
            return reverse_lazy("lecturer_dashboard")
        return reverse_lazy("student_dashboard")


class PresentLogoutView(LogoutView):
    next_page = reverse_lazy("login")


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = RegistrationForm
    role = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect_for_role(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["role"] = self.role
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["role"] = self.role
        context["is_student"] = self.role == User.Role.STUDENT
        return context

    def form_valid(self, form):
        with transaction.atomic():
            user = form.save()
        login(self.request, user)
        return redirect_for_role(user)


class StudentRegisterView(RegisterView):
    role = User.Role.STUDENT


class LecturerRegisterView(RegisterView):
    role = User.Role.LECTURER


class StudentParticipationMixin(StudentRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["participations"] = CourseParticipant.objects.filter(
            student=self.request.user
        ).select_related("course")
        return context


class StudentDashboardView(StudentParticipationMixin, TemplateView):
    template_name = "student/dashboard.html"


class StudentCoursesView(StudentParticipationMixin, TemplateView):
    template_name = "student/courses.html"


class StudentHistoryView(StudentRequiredMixin, TemplateView):
    template_name = "student/history.html"


class PresentPasswordResetView(PasswordResetView):
    form_class = PresentPasswordResetForm
    email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")
    template_name = "registration/password_reset_form.html"


class PresentPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = StyledSetPasswordForm
    success_url = reverse_lazy("password_reset_complete")
    template_name = "registration/password_reset_confirm.html"


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_profile_form(self, data=None):
        user = self.request.user
        if user.is_student:
            return StudentProfileForm(data, instance=user.student_profile)
        profile, _ = LecturerProfile.objects.get_or_create(user=user)
        return LecturerProfileForm(data, instance=profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("user_form", ProfileForm(instance=self.request.user))
        context.setdefault("profile_form", self.get_profile_form())
        return context

    def post(self, request, *args, **kwargs):
        user_form = ProfileForm(request.POST, instance=request.user)
        profile_form = self.get_profile_form(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
        return self.render_to_response(
            self.get_context_data(user_form=user_form, profile_form=profile_form)
        )


class PresentPasswordChangeView(PasswordChangeView):
    form_class = StyledPasswordChangeForm
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        messages.success(self.request, "Password updated.")
        return super().form_valid(form)
