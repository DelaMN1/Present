from django.contrib import messages
from django.db.models import Count, IntegerField, Q, QuerySet, Value
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from accounts.mixins import LecturerRequiredMixin
from courses.forms import CourseDeleteForm, CourseForm
from courses.models import Course, CourseParticipant

SESSION_DURATIONS = {"5", "10", "15", "20"}
SESSION_RADII = {"50", "100", "150", "200"}


def lecturer_courses(user) -> QuerySet[Course]:
    return Course.objects.filter(lecturer=user).annotate(
        participant_count=Count("participants", distinct=True),
        session_count=Value(0, output_field=IntegerField()),
    )


def session_options(request):
    duration = request.GET.get("duration", "10")
    radius = request.GET.get("radius", "100")
    if duration not in SESSION_DURATIONS:
        duration = "10"
    if radius not in SESSION_RADII:
        radius = "100"
    return int(duration), int(radius)


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
            Course.objects.filter(lecturer=self.request.user)
            .order_by("academic_period")
            .values_list("academic_period", flat=True)
            .distinct()
        )

    def _default_period(self):
        latest = (
            Course.objects.filter(lecturer=self.request.user, is_archived=False)
            .order_by("-created_at")
            .first()
        )
        if latest:
            return latest.academic_period
        latest_any = (
            Course.objects.filter(lecturer=self.request.user)
            .order_by("-created_at")
            .first()
        )
        return latest_any.academic_period if latest_any else ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periods = self._periods()
        show_archived = self.request.GET.get("archived") == "1"
        if "period" in self.request.GET:
            selected = self.request.GET.get("period") or ""
        else:
            selected = "" if show_archived else self._default_period()
        owned = lecturer_courses(self.request.user)
        context["periods"] = periods
        context["selected_period"] = selected
        context["show_archived"] = show_archived
        context["has_any_courses"] = owned.exists()
        context["active_course_count"] = owned.filter(is_archived=False).count()
        context["archived_course_count"] = owned.filter(is_archived=True).count()
        context["participant_count"] = (
            CourseParticipant.objects.filter(course__lecturer=self.request.user)
            .values("student")
            .distinct()
            .count()
        )
        context["sessions_today_count"] = 0
        context["checkins_today_count"] = 0
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tab = self.request.GET.get("tab", "overview")
        if tab not in {"overview", "students", "attendance", "sessions"}:
            tab = "overview"
        context["tab"] = tab
        context["participants"] = self.object.participants.select_related(
            "student", "student__student_profile"
        )
        return context


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


class LecturerStudentsView(LecturerRequiredMixin, TemplateView):
    template_name = "lecturer/students.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = CourseParticipant.objects.filter(
            course__lecturer=self.request.user
        ).select_related("student", "student__student_profile", "course")
        q = (self.request.GET.get("q") or "").strip()
        course_filter = self.request.GET.get("course") or ""
        if q:
            qs = qs.filter(
                Q(student__first_name__icontains=q)
                | Q(student__last_name__icontains=q)
                | Q(student__email__icontains=q)
                | Q(student__student_profile__student_id__icontains=q)
            )
        if course_filter:
            qs = qs.filter(course_id=course_filter)
        context["participants"] = qs
        context["courses"] = lecturer_courses(self.request.user).filter(is_archived=False)
        context["q"] = q
        context["course_filter"] = course_filter
        return context


class LecturerAttendanceView(LecturerRequiredMixin, TemplateView):
    template_name = "lecturer/attendance.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["courses"] = lecturer_courses(self.request.user).filter(is_archived=False)
        return context


class LecturerReportsView(LecturerRequiredMixin, TemplateView):
    template_name = "lecturer/reports.html"


class LecturerHelpView(LecturerRequiredMixin, TemplateView):
    template_name = "lecturer/help.html"


class CourseSessionView(LecturerCourseQuerysetMixin, DetailView):
    template_name = "lecturer/session_live.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        duration, radius = session_options(self.request)
        context["duration"] = duration
        context["radius"] = radius
        context["duration_seconds"] = duration * 60
        context["present_count"] = 0
        return context


class CourseSessionEndedView(LecturerCourseQuerysetMixin, DetailView):
    template_name = "lecturer/session_ended.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        duration, radius = session_options(self.request)
        context["duration"] = duration
        context["radius"] = radius
        context["present_count"] = 0
        return context
