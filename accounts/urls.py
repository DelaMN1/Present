from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views
from courses.views import LecturerDashboardView

urlpatterns = [
    path("login/", views.PresentLoginView.as_view(), name="login"),
    path("logout/", views.PresentLogoutView.as_view(), name="logout"),
    path("register/", views.StudentRegisterView.as_view(), name="register"),
    path(
        "register/student/",
        views.StudentRegisterView.as_view(),
        name="register_student",
    ),
    path(
        "register/lecturer/",
        views.LecturerRegisterView.as_view(),
        name="register_lecturer",
    ),
    path(
        "password-reset/",
        views.PresentPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        views.PresentPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "profile/password/",
        views.PresentPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "lecturer/",
        LecturerDashboardView.as_view(),
        name="lecturer_dashboard",
    ),
    path(
        "student/",
        views.StudentDashboardView.as_view(),
        name="student_dashboard",
    ),
]
