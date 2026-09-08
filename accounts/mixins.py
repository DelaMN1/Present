from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

from accounts.models import User


def lecturer_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_lecturer:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped


def student_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_student:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped


class LecturerRequiredMixin:
    @method_decorator(lecturer_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class StudentRequiredMixin:
    @method_decorator(student_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def redirect_for_role(user):
    if user.is_authenticated and user.role == User.Role.LECTURER:
        return redirect("lecturer_dashboard")
    if user.is_authenticated and user.role == User.Role.STUDENT:
        return redirect("student_dashboard")
    return redirect("login")
