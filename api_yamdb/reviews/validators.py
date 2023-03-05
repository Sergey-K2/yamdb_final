import datetime as dt
import re

from django.core.validators import ValidationError
from rest_framework import serializers


def validate_year(value):
    current_year = dt.datetime.now().year
    if not (value <= current_year):
        raise serializers.ValidationError(
            f"Указан неверный год {value}!"
            f"Год должен быть не больше текущего - {current_year}."
        )
    return value


def username_validator(username):
    if username == "me":
        raise ValidationError("You cannot use 'me' as a username")
    invalid_chars = "".join(set(re.sub(r"[\w.@+-]", "", username)))
    if invalid_chars:
        raise ValidationError(
            f"You cannot use this characters - {invalid_chars}."
        )

    return username
