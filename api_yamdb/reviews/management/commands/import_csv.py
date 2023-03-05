import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import Category, Comment, Genre, Review, Title, TitleGenre
from users.models import CustomUser

CSV_PATH = os.path.join(settings.BASE_DIR, "static/data")

CSV_FILES_DATA = {
    "category.csv": Category,
    "comments.csv": Comment,
    "genre.csv": Genre,
    "genre_title.csv": TitleGenre,
    "titles.csv": Title,
    "review.csv": Review,
    "users.csv": CustomUser,
}


class Command(BaseCommand):
    help = "Imports data from csv files to database"

    def import_file(self, Model, csv_file):
        r_file = str(os.path.join(CSV_PATH, csv_file))
        with open(r_file, encoding="utf-8"):
            file_reader = csv.reader(r_file, delimiter=",")
            count = 0
            for row in file_reader:
                if count == 0:
                    fields = row
                else:
                    data = dict(zip(fields, row))
                    Model.objects.get_or_create(**data).save()
                count += 1

    def handler(self, *args, **options):
        for csv_file, Model in CSV_FILES_DATA.items():
            self.import_file(csv_file, Model)
