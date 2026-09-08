from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import LecturerProfile, StudentProfile, User

UserModel = get_user_model()


@override_settings(
    STUDENT_EMAIL_DOMAINS=["st.ug.edu.gh"],
    LECTURER_EMAIL_DOMAINS=["ug.edu.gh"],
)
class ProfileTests(TestCase):
    def setUp(self):
        self.student = UserModel.objects.create_user(
            email="ama@st.ug.edu.gh",
            password="Str0ng-present-pass",
            role=User.Role.STUDENT,
            first_name="Ama",
            last_name="Boateng",
        )
        StudentProfile.objects.create(user=self.student, student_id="10982346")
        self.lecturer = UserModel.objects.create_user(
            email="mensah@ug.edu.gh",
            password="Str0ng-present-pass",
            role=User.Role.LECTURER,
            first_name="Kwame",
            last_name="Mensah",
        )
        LecturerProfile.objects.create(user=self.lecturer)

    def test_student_can_update_name_but_not_student_id(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("profile"),
            {
                "first_name": "Ama-updated",
                "last_name": "Boateng",
                "email": "ama@st.ug.edu.gh",
                "programme": "Biochemistry",
                "level": "300",
                "department": "Biological Sciences",
                "student_id": "00000000",
            },
        )
        self.assertRedirects(response, reverse("profile"))
        self.student.refresh_from_db()
        self.student.student_profile.refresh_from_db()
        self.assertEqual(self.student.first_name, "Ama-updated")
        self.assertEqual(self.student.student_profile.student_id, "10982346")
        self.assertEqual(self.student.student_profile.programme, "Biochemistry")

    def test_student_cannot_change_email_off_domain(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("profile"),
            {
                "first_name": "Ama",
                "last_name": "Boateng",
                "email": "ama@gmail.com",
                "programme": "",
                "level": "",
                "department": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.email, "ama@st.ug.edu.gh")

    def test_lecturer_can_update_department(self):
        self.client.force_login(self.lecturer)
        response = self.client.post(
            reverse("profile"),
            {
                "first_name": "Kwame",
                "last_name": "Mensah",
                "email": "mensah@ug.edu.gh",
                "staff_id": "STF-1",
                "department": "Biochemistry",
            },
        )
        self.assertRedirects(response, reverse("profile"))
        self.lecturer.lecturer_profile.refresh_from_db()
        self.assertEqual(self.lecturer.lecturer_profile.staff_id, "STF-1")
        self.assertEqual(self.lecturer.lecturer_profile.department, "Biochemistry")
