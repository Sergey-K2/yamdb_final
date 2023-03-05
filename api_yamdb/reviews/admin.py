from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from reviews.models import Category, Comment, CustomUser, Genre, Review, Title


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("pk", "username", "email", "role")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "role",
                    "bio",
                    "confirmation_code",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_editable = [
        "email",
        "role",
    ]
    search_fields = ("username",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "name")
    search_fields = ("slug",)
    list_filter = ("slug",)
    empty_value_display = "-пусто-"


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ("name", "year", "category")
    search_fields = ("name",)
    list_filter = ("category",)
    empty_value_display = "-пусто-"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author", "title", "text", "score", "pub_date")
    search_fields = ("title",)
    list_filter = ("author", "title")
    empty_value_display = "-пусто-"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "review", "text", "pub_date")
    search_fields = ("review",)
    list_filter = ("author", "review")
    empty_value_display = "-пусто-"


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
