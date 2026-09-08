#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "test":
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
    else:
        # Cursor (and some shells) export test settings. Never use those for
        # runserver, migrate, or other non-test commands.
        current = os.environ.get("DJANGO_SETTINGS_MODULE", "")
        if not current or current == "config.settings.test":
            os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Is the virtual environment active?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
