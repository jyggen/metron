import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from comicsdb.models import (
    Announcement,
    Arc,
    Attribution,
    Character,
    Creator,
    Credits,
    Genre,
    Imprint,
    Issue,
    Publisher,
    Rating,
    Role,
    Series,
    SeriesType,
    Team,
    Universe,
    Variant,
)

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.django.Password("password")


class GenreFactory(DjangoModelFactory):
    class Meta:
        model = Genre

    name = factory.Sequence(lambda n: f"Genre {n}")


class RatingFactory(DjangoModelFactory):
    class Meta:
        model = Rating

    name = factory.Sequence(lambda n: f"Rating {n}")
    short_description = factory.Faker("sentence")


class SeriesTypeFactory(DjangoModelFactory):
    class Meta:
        model = SeriesType

    name = factory.Sequence(lambda n: f"Series Type {n}")


class PublisherFactory(DjangoModelFactory):
    class Meta:
        model = Publisher

    name = factory.Sequence(lambda n: f"Publisher {n}")
    founded = factory.Faker("pyint", min_value=1900, max_value=2025)
    country = "US"
    created_by = factory.LazyFunction(lambda: User.objects.first() or UserFactory())
    edited_by = factory.LazyAttribute(lambda obj: obj.created_by)


class ImprintFactory(DjangoModelFactory):
    class Meta:
        model = Imprint

    name = factory.Sequence(lambda n: f"Imprint {n}")
    publisher = factory.SubFactory(PublisherFactory)
    created_by = factory.LazyFunction(lambda: User.objects.first() or UserFactory())
    edited_by = factory.LazyAttribute(lambda obj: obj.created_by)


class UniverseFactory(DjangoModelFactory):
    class Meta:
        model = Universe

    name = factory.Sequence(lambda n: f"Universe {n}")
    publisher = factory.SubFactory(PublisherFactory)
    designation = factory.Faker("word")
    created_by = factory.LazyFunction(lambda: User.objects.first() or UserFactory())
    edited_by = factory.LazyAttribute(lambda obj: obj.created_by)


class ArcFactory(DjangoModelFactory):
    class Meta:
        model = Arc

    name = factory.Sequence(lambda n: f"Arc {n}")
    created_by = factory.LazyFunction(lambda: User.objects.first() or UserFactory())
    edited_by = factory.LazyAttribute(lambda obj: obj.created_by)


class CreatorFactory(DjangoModelFactory):
    class Meta:
        model = Creator

    name = factory.Faker("name")
    created_by = factory.LazyFunction(lambda: User.objects.first() or UserFactory())
    edited_by = factory.LazyAttribute(lambda obj: obj.created_by)


class TeamFactory(DjangoModelFactory):
    class Meta:
        model = Team

    name = factory.Sequence(lambda n: f"Team {n}")
    created_by = factory.LazyFunction(lambda: User.objects.first() or UserFactory())
    edited_by = factory.LazyAttribute(lambda obj: obj.created_by)


class CharacterFactory(DjangoModelFactory):
    class Meta:
        model = Character

    name = factory.Sequence(lambda n: f"Character {n}")
    created_by = factory.LazyFunction(lambda: User.objects.first() or UserFactory())
    edited_by = factory.LazyAttribute(lambda obj: obj.created_by)


class SeriesFactory(DjangoModelFactory):
    class Meta:
        model = Series

    name = factory.Sequence(lambda n: f"Series {n}")
    sort_name = factory.LazyAttribute(lambda obj: obj.name)
    volume = 1
    year_began = factory.Faker("pyint", min_value=1938, max_value=2025)
    series_type = factory.SubFactory(SeriesTypeFactory)
    publisher = factory.SubFactory(PublisherFactory)
    created_by = factory.LazyFunction(lambda: User.objects.first() or UserFactory())
    edited_by = factory.LazyAttribute(lambda obj: obj.created_by)


class IssueFactory(DjangoModelFactory):
    class Meta:
        model = Issue

    series = factory.SubFactory(SeriesFactory)
    number = factory.Sequence(lambda n: str(n + 1))
    cover_date = factory.Faker("date_object")
    rating = factory.LazyFunction(lambda: Rating.objects.first() or RatingFactory())
    created_by = factory.LazyFunction(lambda: User.objects.first() or UserFactory())
    edited_by = factory.LazyAttribute(lambda obj: obj.created_by)


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role

    name = factory.Sequence(lambda n: f"Role {n}")
    order = factory.Sequence(lambda n: n)


class CreditsFactory(DjangoModelFactory):
    class Meta:
        model = Credits

    issue = factory.SubFactory(IssueFactory)
    creator = factory.SubFactory(CreatorFactory)


class VariantFactory(DjangoModelFactory):
    class Meta:
        model = Variant

    issue = factory.SubFactory(IssueFactory)
    image = factory.django.ImageField()
    name = factory.Sequence(lambda n: f"Variant {n}")


class AttributionFactory(DjangoModelFactory):
    class Meta:
        model = Attribution
        exclude = ["content_object"]

    source = Attribution.Source.WIKIPEDIA
    url = factory.Faker("url")
    content_object = factory.SubFactory(PublisherFactory)
    content_type = factory.LazyAttribute(
        lambda obj: Attribution.content_type.field.related_model.objects.get_for_model(
            obj.content_object
        )
    )
    object_id = factory.LazyAttribute(lambda obj: obj.content_object.pk)


class AnnouncementFactory(DjangoModelFactory):
    class Meta:
        model = Announcement

    title = factory.Faker("sentence")
    content = factory.Faker("paragraph")
    active = True