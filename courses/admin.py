from django.contrib import admin

from courses.models import Course, CourseParticipant


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "academic_period",
        "lecturer",
        "is_archived",
        "created_at",
    )
    list_filter = ("academic_period", "is_archived", "lecturer")
    search_fields = ("code", "name", "lecturer__email")


@admin.register(CourseParticipant)
class CourseParticipantAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "first_seen_at")
    list_filter = ("course",)
    search_fields = (
        "student__email",
        "student__student_profile__student_id",
        "course__code",
    )
