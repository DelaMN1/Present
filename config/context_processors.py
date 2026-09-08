from django.utils import timezone


def appearance(request):
    hour = timezone.localtime().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    user = request.user
    initials = "P"
    if getattr(user, "is_authenticated", False) and user.is_authenticated:
        first = (user.first_name or "").strip()
        last = (user.last_name or "").strip()
        if first and last:
            initials = (first[0] + last[0]).upper()
        elif first:
            initials = first[:2].upper()
        elif user.email:
            initials = user.email[:2].upper()

    return {
        "greeting": greeting,
        "today": timezone.localtime().date(),
        "user_initials": initials,
    }
