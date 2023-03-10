from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, SignUpView, TitleViewSet, TokenView,
                       UserViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "api"

v1_router = DefaultRouter()

v1_router.register(r"titles", TitleViewSet, basename="titles")
v1_router.register(r"genres", GenreViewSet, basename="genres")
v1_router.register(r"categories", CategoryViewSet, basename="categories")
v1_router.register(r"users", UserViewSet, basename="user")
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)

registration_and_auth_urls = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("token/", TokenView.as_view(), name="login"),
]

urlpatterns = [
    path("v1/", include(v1_router.urls)),
    path("v1/auth/", include(registration_and_auth_urls)),
]
