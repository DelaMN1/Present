from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import LecturerProfile, StudentProfile, User

UserModel = get_user_model()


@override_settings(
    STUDENT_EMAIL_DOMAINS=["st.ug.edu.gh"],
    LECTURER_EMAIL_DOMAINS=["ug.edu.gh"],
)
class RegistrationTests(TestCase):
    def test_student_can_register_with_campus_email(self):
        response = self.client.post(
            reverse("register_student"),
            {
                "first_name": "Ama",
                "last_name": "Boateng",
                "email": "ama@st.ug.edu.gh",
                "student_id": "10982346",
                "password1": "Str0ng-present-pass",
                "password2": "Str0ng-present-pass",
            },
        )
        self.assertRedirects(response, reverse("student_dashboard"))
        user = UserModel.objects.get(email="ama@st.ug.edu.gh")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertEqual(user.student_profile.student_id, "10982346")

    def test_student_gmail_is_rejected(self):
        response = self.client.post(
            reverse("register_student"),
            {
                "first_name": "Ama",
                "last_name": "Boateng",
                "email": "ama@gmail.com",
                "student_id": "10982346",
                "password1": "Str0ng-present-pass",
                "password2": "Str0ng-present-pass",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserModel.objects.exists())
        self.assertContains(response, "email domain is not allowed")

    def test_lecturer_can_register_with_staff_email(self):
        response = self.client.post(
            reverse("register_lecturer"),
            {
                "first_name": "Kwame",
                "last_name": "Mensah",
                "email": "mensah@ug.edu.gh",
                "password1": "Str0ng-present-pass",
                "password2": "Str0ng-present-pass",
            },
        )
        self.assertRedirects(response, reverse("lecturer_dashboard"))
        user = UserModel.objects.get(email="mensah@ug.edu.gh")
        self.assertEqual(user.role, User.Role.LECTURER)
        self.assertTrue(LecturerProfile.objects.filter(user=user).exists())

    def test_lecturer_student_domain_is_rejected(self):
        response = self.client.post(
            reverse("register_lecturer"),
            {
                "first_name": "Kwame",
                "last_name": "Mensah",
                "email": "mensah@st.ug.edu.gh",
                "password1": "Str0ng-present-pass",
                "password2": "Str0ng-present-pass",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserModel.objects.exists())

    def test_duplicate_student_id_is_rejected(self):
        UserModel.objects.create_user(
            email="first@st.ug.edu.gh",
            password="Str0ng-present-pass",
            role=User.Role.STUDENT,
            first_name="John",
            last_name="Mensah",
        )
        StudentProfile.objects.create(
            user=UserModel.objects.get(email="first@st.ug.edu.gh"),
            student_id="10982345",
        )
        response = self.client.post(
            reverse("register_student"),
            {
                "first_name": "Jane",
                "last_name": "Mensah",
                "email": "jane@st.ug.edu.gh",
                "student_id": "10982345",
                "password1": "Str0ng-present-pass",
                "password2": "Str0ng-present-pass",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserModel.objects.filter(email="jane@st.ug.edu.gh").exists())

    def test_student_id_cannot_change_after_save(self):
        user = UserModel.objects.create_user(
            email="ama@st.ug.edu.gh",
            password="Str0ng-present-pass",
            role=User.Role.STUDENT,
        )
        profile = StudentProfile.objects.create(user=user, student_id="10982346")
        profile.student_id = "00000000"
        with self.assertRaises(ValidationError):
            profile.save()

    def test_login_with_email(self):
        UserModel.objects.create_user(
            email="mensah@ug.edu.gh",
            password="Str0ng-present-pass",
            role=User.Role.LECTURER,
            first_name="Kwame",
        )
        LecturerProfile.objects.create(user=UserModel.objects.get(email="mensah@ug.edu.gh"))
        response = self.client.post(
            reverse("login"),
            {"username": "mensah@ug.edu.gh", "password": "Str0ng-present-pass"},
        )
        self.assertRedirects(response, reverse("lecturer_dashboard"))

    def test_student_cannot_open_lecturer_dashboard(self):
        user = UserModel.objects.create_user(
            email="ama@st.ug.edu.gh",
            password="Str0ng-present-pass",
            role=User.Role.STUDENT,
        )
        StudentProfile.objects.create(user=user, student_id="10982346")
        self.client.force_login(user)
        response = self.client.get(reverse("lecturer_dashboard"))
        self.assertEqual(response.status_code, 403)
