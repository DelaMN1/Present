from django.apps import AppConfig
from django.contrib import admin


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Accounts"

    def ready(self):
        admin.site.site_header = "Present administration"
        admin.site.site_title = "Present"
        admin.site.index_title = "Administration"
