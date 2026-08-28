from django.conf import settings
from django.db import models


class Course(models.Model):
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        limit_choices_to={"role": "LECTURER"},
    )
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    academic_period = models.CharField(max_length=64)
    is_archived = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["lecturer", "code", "academic_period"],
                name="unique_lecturer_course_period",
            ),
        ]
        indexes = [
            models.Index(fields=["lecturer", "academic_period"]),
        ]
        ordering = ["code", "name"]

    def __str__(self):
        return f"{self.code} — {self.name}"

    def save(self, *args, **kwargs):
        self.code = self.code.strip()
        self.name = self.name.strip()
        self.academic_period = self.academic_period.strip()
        super().save(*args, **kwargs)


class CourseParticipant(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_participations",
        limit_choices_to={"role": "STUDENT"},
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="participants",
    )
    first_seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course_participant",
            ),
        ]

    def __str__(self):
        return f"{self.student} in {self.course.code}"
