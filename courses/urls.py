from django.urls import path

from courses import views

urlpatterns = [
    path("courses/", views.CourseListView.as_view(), name="course_list"),
    path(
        "lecturer/students/",
        views.LecturerStudentsView.as_view(),
        name="lecturer_students",
    ),
    path(
        "lecturer/attendance/",
        views.LecturerAttendanceView.as_view(),
        name="lecturer_attendance",
    ),
    path(
        "lecturer/reports/",
        views.LecturerReportsView.as_view(),
        name="lecturer_reports",
    ),
    path("lecturer/help/", views.LecturerHelpView.as_view(), name="lecturer_help"),
    path("courses/create/", views.CourseCreateView.as_view(), name="course_create"),
    path("courses/<int:pk>/", views.CourseDetailView.as_view(), name="course_detail"),
    path(
        "courses/<int:pk>/session/",
        views.CourseSessionView.as_view(),
        name="course_session",
    ),
    path(
        "courses/<int:pk>/session/ended/",
        views.CourseSessionEndedView.as_view(),
        name="course_session_ended",
    ),
    path("courses/<int:pk>/edit/", views.CourseUpdateView.as_view(), name="course_edit"),
    path(
        "courses/<int:pk>/archive/",
        views.CourseArchiveView.as_view(),
        name="course_archive",
    ),
    path(
        "courses/<int:pk>/delete/",
        views.CourseDeleteView.as_view(),
        name="course_delete",
    ),
]
