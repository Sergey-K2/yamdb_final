import random

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status
from rest_framework.decorators import action, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (
    IsAdmin,
    IsAdminOrModerOrAuthorOrReadOnly,
    IsAdminOrReadOnly,
)
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleGetSerializer,
    TitlePostSerializer,
    TokenSerializer,
    UserSerializer,
    UserProfileSerializer,
)
from reviews.models import Category, CustomUser, Genre, Review, Title


class GenreCategoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = LimitOffsetPagination
    search_fields = ("name",)
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    class Meta:
        abstract = True


def create_confirm_code():
    return "".join(
        random.choices(
            settings.CONFIRM_CODE_CHARS, k=settings.CONFIRM_CODE_LENGTH
        )
    )


def send_confirm_code(email, confirm_code):
    send_mail(
        subject="Код подтверждения",
        message=f"Код подтверждения\n{confirm_code}",
        recipient_list=[email],
        from_email=settings.EMAIL_HOST_USER,
    )


class SignUpView(APIView):
    @permission_classes(AllowAny)
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        username = serializer.validated_data.get("username")
        try:
            user, created = CustomUser.objects.get_or_create(
                username=username, email=email
            )
        except IntegrityError:
            return Response(
                "User with same username or email already exists",
                status=status.HTTP_400_BAD_REQUEST,
            )
        confirm_code = create_confirm_code()
        user.confirmation_code = confirm_code
        user.save()
        send_confirm_code(email=email, confirm_code=confirm_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    @permission_classes(AllowAny)
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        confirm_code = serializer.validated_data.get("confirmation_code")
        user = get_object_or_404(CustomUser, username=username)
        if (user.confirmation_code != confirm_code
                or confirm_code == settings.CONFIRM_CODE_STUB):
            if confirm_code != settings.CONFIRM_CODE_STUB:
                user.confirmation_code = settings.CONFIRM_CODE_STUB
                user.save()
            return Response(
                "Invalid confirm code", status=status.HTTP_400_BAD_REQUEST
            )

        token = AccessToken.for_user(user)
        return Response({"access": str(token)})


class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    lookup_field = "username"
    search_fields = ("username",)
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=["get", "patch"],
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def user_profile(self, request):
        user = request.user
        if request.method == "GET":
            return Response(UserProfileSerializer(user).data)
        serializer = UserProfileSerializer(
            user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg("reviews__score"))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = LimitOffsetPagination
    filterset_fileds = (
        "name",
        "year",
        "genre__slug",
        "category__slug",
    )
    filterset_class = TitleFilter
    ordering = ("rating", "name")

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return TitleGetSerializer
        return TitlePostSerializer


class GenreViewSet(GenreCategoryViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(GenreCategoryViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrModerOrAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrModerOrAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get("review_id"))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
