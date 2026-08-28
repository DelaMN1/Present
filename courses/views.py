from django.contrib import messages
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)

from accounts.mixins import LecturerRequiredMixin
from courses.forms import CourseDeleteForm, CourseForm
from courses.models import Course


def lecturer_courses(user) -> QuerySet[Course]:
    return Course.objects.filter(lecturer=user)


class LecturerCourseQuerysetMixin(LecturerRequiredMixin):
    def get_queryset(self):
        return lecturer_courses(self.request.user)


class LecturerDashboardView(LecturerCourseQuerysetMixin, ListView):
    template_name = "lecturer/dashboard.html"
    context_object_name = "courses"

    def get_queryset(self):
        qs = super().get_queryset()
        period = self.request.GET.get("period")
        show_archived = self.request.GET.get("archived") == "1"
        if not show_archived:
            qs = qs.filter(is_archived=False)
        if period:
            qs = qs.filter(academic_period=period)
        elif "period" not in self.request.GET and not show_archived:
            default_period = self._default_period()
            if default_period:
                qs = qs.filter(academic_period=default_period)
        return qs

    def _periods(self):
        return list(
            lecturer_courses(self.request.user)
            .order_by("academic_period")
            .values_list("academic_period", flat=True)
            .distinct()
        )

    def _default_period(self):
        latest = (
            lecturer_courses(self.request.user)
            .filter(is_archived=False)
            .order_by("-created_at")
            .first()
        )
        if latest:
            return latest.academic_period
        latest_any = lecturer_courses(self.request.user).order_by("-created_at").first()
        return latest_any.academic_period if latest_any else ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periods = self._periods()
        show_archived = self.request.GET.get("archived") == "1"
        if "period" in self.request.GET:
            selected = self.request.GET.get("period") or ""
        else:
            selected = "" if show_archived else self._default_period()
        context["periods"] = periods
        context["selected_period"] = selected
        context["show_archived"] = show_archived
        context["has_any_courses"] = lecturer_courses(self.request.user).exists()
        return context


class CourseListView(LecturerDashboardView):
    template_name = "courses/course_list.html"


class CourseCreateView(LecturerRequiredMixin, CreateView):
    form_class = CourseForm
    template_name = "courses/course_form.html"
    success_url = reverse_lazy("lecturer_dashboard")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance.lecturer = self.request.user
        return form

    def form_valid(self, form):
        messages.success(self.request, "Course created.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create course"
        return context


class CourseDetailView(LecturerCourseQuerysetMixin, DetailView):
    template_name = "courses/course_detail.html"
    context_object_name = "course"


class CourseUpdateView(LecturerCourseQuerysetMixin, UpdateView):
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def get_success_url(self):
        return reverse("course_detail", args=[self.object.pk])

    def form_valid(self, form):
        messages.success(self.request, "Course updated.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit course"
        return context


class CourseArchiveView(LecturerRequiredMixin, View):
    def post(self, request, pk):
        course = get_object_or_404(lecturer_courses(request.user), pk=pk)
        course.is_archived = not course.is_archived
        course.save(update_fields=["is_archived", "updated_at"])
        if course.is_archived:
            messages.success(request, f"{course.code} archived.")
        else:
            messages.success(request, f"{course.code} restored to the dashboard.")
        return redirect("lecturer_dashboard")

    def get(self, request, *args, **kwargs):
        return redirect("course_detail", pk=kwargs["pk"])


class CourseDeleteView(LecturerCourseQuerysetMixin, FormView):
    template_name = "courses/course_confirm_delete.html"
    form_class = CourseDeleteForm

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(lecturer_courses(request.user), pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["course"] = self.course
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course
        return context

    def form_valid(self, form):
        code = self.course.code
        self.course.delete()
        messages.success(self.request, f"{code} deleted.")
        return redirect("lecturer_dashboard")
