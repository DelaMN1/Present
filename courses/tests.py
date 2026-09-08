from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import LecturerProfile, StudentProfile, User
from courses.models import Course

UserModel = get_user_model()


class CourseTests(TestCase):
    def setUp(self):
        self.lecturer = UserModel.objects.create_user(
            email="mensah@ug.edu.gh",
            password="Str0ng-present-pass",
            role=User.Role.LECTURER,
            first_name="Kwame",
        )
        LecturerProfile.objects.create(user=self.lecturer)
        self.other = UserModel.objects.create_user(
            email="other@ug.edu.gh",
            password="Str0ng-present-pass",
            role=User.Role.LECTURER,
            first_name="Ama",
        )
        LecturerProfile.objects.create(user=self.other)
        self.student = UserModel.objects.create_user(
            email="ama@st.ug.edu.gh",
            password="Str0ng-present-pass",
            role=User.Role.STUDENT,
        )
        StudentProfile.objects.create(user=self.student, student_id="10982346")

    def _create_course(self, lecturer=None, **kwargs):
        data = {
            "code": "BIOC 301",
            "name": "Clinical Biochemistry",
            "academic_period": "2026/2027 First Semester",
            "description": "",
        }
        data.update(kwargs)
        return Course.objects.create(lecturer=lecturer or self.lecturer, **data)

    def test_lecturer_can_create_course(self):
        self.client.force_login(self.lecturer)
        response = self.client.post(
            reverse("course_create"),
            {
                "code": "BIOC 301",
                "name": "Clinical Biochemistry",
                "academic_period": "2026/2027 First Semester",
                "description": "Core course",
            },
        )
        self.assertRedirects(response, reverse("lecturer_dashboard"))
        course = Course.objects.get(code="BIOC 301")
        self.assertEqual(course.lecturer, self.lecturer)
        self.assertEqual(course.name, "Clinical Biochemistry")

    def test_duplicate_code_in_same_period_is_rejected(self):
        self._create_course()
        self.client.force_login(self.lecturer)
        response = self.client.post(
            reverse("course_create"),
            {
                "code": "BIOC 301",
                "name": "Clinical Biochemistry Repeat",
                "academic_period": "2026/2027 First Semester",
                "description": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Course.objects.filter(lecturer=self.lecturer).count(), 1)

    def test_another_lecturer_can_reuse_code(self):
        self._create_course()
        self.client.force_login(self.other)
        response = self.client.post(
            reverse("course_create"),
            {
                "code": "BIOC 301",
                "name": "Clinical Biochemistry",
                "academic_period": "2026/2027 First Semester",
                "description": "",
            },
        )
        self.assertRedirects(response, reverse("lecturer_dashboard"))
        self.assertEqual(Course.objects.filter(code="BIOC 301").count(), 2)

    def test_student_cannot_create_course(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("course_create"))
        self.assertEqual(response.status_code, 403)

    def test_lecturer_cannot_open_another_lecturers_course(self):
        course = self._create_course()
        self.client.force_login(self.other)
        response = self.client.get(reverse("course_detail", args=[course.pk]))
        self.assertEqual(response.status_code, 404)

    def test_archive_hides_from_default_dashboard(self):
        course = self._create_course()
        self.client.force_login(self.lecturer)
        response = self.client.post(reverse("course_archive", args=[course.pk]))
        self.assertRedirects(response, reverse("lecturer_dashboard"))
        course.refresh_from_db()
        self.assertTrue(course.is_archived)
        dashboard = self.client.get(reverse("lecturer_dashboard"))
        self.assertNotContains(dashboard, "Clinical Biochemistry")
        archived = self.client.get(reverse("lecturer_dashboard") + "?archived=1")
        self.assertContains(archived, "Clinical Biochemistry")

    def test_delete_requires_matching_code(self):
        course = self._create_course()
        self.client.force_login(self.lecturer)
        response = self.client.post(
            reverse("course_delete", args=[course.pk]),
            {"confirmation": "WRONG"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Course.objects.filter(pk=course.pk).exists())

    def test_delete_with_typed_code_removes_course(self):
        course = self._create_course()
        self.client.force_login(self.lecturer)
        response = self.client.post(
            reverse("course_delete", args=[course.pk]),
            {"confirmation": "BIOC 301"},
        )
        self.assertRedirects(response, reverse("lecturer_dashboard"))
        self.assertFalse(Course.objects.filter(pk=course.pk).exists())

    def test_period_filter_defaults_to_latest_non_archived(self):
        self._create_course(academic_period="2025/2026 Second Semester")
        newer = self._create_course(
            code="BIOC 401",
            name="Advanced Biochemistry",
            academic_period="2026/2027 First Semester",
        )
        self.client.force_login(self.lecturer)
        response = self.client.get(reverse("lecturer_dashboard"))
        self.assertContains(response, newer.name)
        self.assertNotContains(response, "Clinical Biochemistry")
