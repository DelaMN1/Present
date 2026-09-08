from django.test import SimpleTestCase, override_settings

from accounts.domains import allowed_domains_for_role, email_domain, email_domain_allowed
from accounts.models import User


class DomainHelperTests(SimpleTestCase):
    def test_email_domain_extracts_host(self):
        self.assertEqual(email_domain("John@ST.UG.EDU.GH"), "st.ug.edu.gh")

    def test_email_domain_rejects_malformed(self):
        self.assertEqual(email_domain("not-an-email"), "")

    @override_settings(
        STUDENT_EMAIL_DOMAINS=["st.ug.edu.gh"],
        LECTURER_EMAIL_DOMAINS=["ug.edu.gh"],
    )
    def test_student_gmail_rejected(self):
        self.assertFalse(email_domain_allowed("ama@gmail.com", User.Role.STUDENT))

    @override_settings(
        STUDENT_EMAIL_DOMAINS=["st.ug.edu.gh"],
        LECTURER_EMAIL_DOMAINS=["ug.edu.gh"],
    )
    def test_student_campus_email_allowed(self):
        self.assertTrue(email_domain_allowed("10982345@st.ug.edu.gh", User.Role.STUDENT))

    @override_settings(
        STUDENT_EMAIL_DOMAINS=["st.ug.edu.gh"],
        LECTURER_EMAIL_DOMAINS=["ug.edu.gh"],
    )
    def test_lecturer_cannot_use_student_domain(self):
        self.assertFalse(email_domain_allowed("doc@st.ug.edu.gh", User.Role.LECTURER))

    @override_settings(
        STUDENT_EMAIL_DOMAINS=["st.ug.edu.gh"],
        LECTURER_EMAIL_DOMAINS=["ug.edu.gh"],
    )
    def test_lecturer_staff_domain_allowed(self):
        self.assertTrue(email_domain_allowed("mensah@ug.edu.gh", User.Role.LECTURER))

    @override_settings(
        STUDENT_EMAIL_DOMAINS=["st.ug.edu.gh"],
        LECTURER_EMAIL_DOMAINS=["ug.edu.gh"],
    )
    def test_allowed_domains_for_role(self):
        self.assertEqual(allowed_domains_for_role(User.Role.STUDENT), ["st.ug.edu.gh"])
        self.assertEqual(allowed_domains_for_role(User.Role.LECTURER), ["ug.edu.gh"])
