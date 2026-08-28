from django.conf import settings

from accounts.models import User


def normalize_domain(value: str) -> str:
    return value.strip().lower().lstrip("@")


def email_domain(email: str) -> str:
    if not email or "@" not in email:
        return ""
    return email.rsplit("@", 1)[-1].strip().lower()


def allowed_domains_for_role(role: str) -> list[str]:
    if role == User.Role.STUDENT:
        return [normalize_domain(d) for d in settings.STUDENT_EMAIL_DOMAINS]
    if role == User.Role.LECTURER:
        return [normalize_domain(d) for d in settings.LECTURER_EMAIL_DOMAINS]
    return []


def email_domain_allowed(email: str, role: str) -> bool:
    domain = email_domain(email)
    return bool(domain) and domain in allowed_domains_for_role(role)
