from django_filters import rest_framework as rest_framework_filters

from reviews.models import Title


class TitleFilter(rest_framework_filters.FilterSet):
    category = rest_framework_filters.CharFilter(field_name="category__slug")
    genre = rest_framework_filters.CharFilter(field_name="genre__slug")

    class Meta:
        model = Title
        fields = "__all__"
