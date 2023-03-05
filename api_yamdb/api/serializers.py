from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from reviews.models import (
    Category,
    Comment,
    CustomUser,
    Genre,
    Review,
    Title,
)
from reviews.validators import username_validator, validate_year


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.MAX_USERNAME_LENGTH,
        required=True,
        validators=[
            username_validator,
        ],
    )
    email = serializers.EmailField(
        required=True, max_length=settings.MAX_EMAIL_LENGTH
    )


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.MAX_USERNAME_LENGTH,
        required=True,
        validators=[
            username_validator,
        ],
    )
    confirmation_code = serializers.CharField(
        max_length=settings.CONFIRM_CODE_LENGTH,
        required=True,
    )


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "bio",
            "role",
        )

    def validate_username(self, username):
        return username_validator(username)


class UserProfileSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ("role",)


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ("slug", "name")


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ("slug", "name")


class TitleGetSerializer(ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "genre",
            "category",
            "rating",
            "description",
        )
        read_only_fields = fields


class TitlePostSerializer(ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field="slug", queryset=Genre.objects.all(), many=True
    )
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "genre",
            "category",
            "description",
        )

    def validate_year(self, value):
        return validate_year(value)


class ReviewSerializer(ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    score = serializers.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")

    def validate(self, data):
        if self.context["request"].method != "POST":
            return data
        if Review.objects.filter(
            title=get_object_or_404(
                Title, pk=self.context["view"].kwargs.get("title_id")
            ),
            author=self.context["request"].user,
        ).exists():
            raise serializers.ValidationError(
                "Можно оставлять только один отзыв!"
            )
        return data


class CommentSerializer(ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")
