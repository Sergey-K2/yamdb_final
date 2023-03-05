from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import username_validator, validate_year

USER_ROLE = "user"
MODERATOR_ROLE = "moderator"
ADMIN_ROLE = "admin"

ROLES = (
    (USER_ROLE, "user"),
    (MODERATOR_ROLE, "moderator"),
    (ADMIN_ROLE, "admin"),
)


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
        max_length=settings.MAX_EMAIL_LENGTH,
    )

    username = models.CharField(
        unique=True,
        null=False,
        blank=False,
        max_length=settings.MAX_USERNAME_LENGTH,
        validators=(username_validator,),
    )

    bio = models.TextField(
        null=True,
        blank=True,
    )

    confirmation_code = models.CharField(
        null=True, blank=True, max_length=settings.CONFIRM_CODE_LENGTH
    )

    role = models.CharField(
        choices=ROLES,
        max_length=max(len(role) for role, _ in ROLES),
        default=USER_ROLE,
    )

    def is_admin(self):
        return self.role == ADMIN_ROLE or self.is_staff

    def is_moderator(self):
        return self.role == MODERATOR_ROLE

    def __str__(self):
        return self.username

    class Meta:
        ordering = ("username",)

    REQUIRED_FIELDS = ("email",)
    USERNAME_FIELD = "username"


class GenreCategory(models.Model):
    name = models.CharField(
        verbose_name="Название",
        max_length=256,
    )
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        ordering = ("name",)
        abstract = True

    def __str__(self):
        return self.name


class Genre(GenreCategory):
    class Meta(GenreCategory.Meta):
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Category(GenreCategory):
    description = models.TextField(verbose_name="Описание", blank=True)

    class Meta(GenreCategory.Meta):
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Title(models.Model):
    name = models.CharField(
        verbose_name="Название произведения", max_length=256
    )
    genre = models.ManyToManyField(
        Genre,
        null=True,
        related_name="titles",
        verbose_name="Жанр",
        help_text="Жанр, к которому будет относиться произведение",
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name="titles",
        verbose_name="Категория",
        help_text="Категория, к которой будет относиться пост",
    )
    description = models.TextField(verbose_name="Описание")
    year = models.PositiveIntegerField(
        verbose_name="Год выпуска", validators=(validate_year,)
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Произведение"
        verbose_name_plural = "Прозведения"

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    title = models.ForeignKey(Title, null=True, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, null=True, on_delete=models.CASCADE)


class CommentReview(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="Автор"
    )
    pub_date = models.DateTimeField(
        "Дата публикации отзыва", auto_now_add=True
    )
    text = models.TextField(verbose_name="Текст")

    class Meta:
        abstract = True
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text[:15]


class Review(CommentReview):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Произведение",
    )
    score = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(10)),
        verbose_name="Оценка",
        error_messages={"validators": "Оценки могут быть от 1 до 10"},
        default=1,
    )

    class Meta(CommentReview.Meta):
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_author"
            )
        ]
        default_related_name = "reviews"


class Comment(CommentReview):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name="Отзыв",
    )

    class Meta(CommentReview.Meta):
        verbose_name = "Коментарий"
        verbose_name_plural = "Коментарии"
        default_related_name = "comments"
