from django.core.management.base import BaseCommand

from comicsdb.factories import (
    ArcFactory,
    CharacterFactory,
    CreatorFactory,
    CreditsFactory,
    GenreFactory,
    ImprintFactory,
    IssueFactory,
    PublisherFactory,
    RatingFactory,
    RoleFactory,
    SeriesFactory,
    SeriesTypeFactory,
    TeamFactory,
    UniverseFactory,
    UserFactory,
    VariantFactory,
)


class Command(BaseCommand):
    help = "Seed the database with development data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing data before seeding",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing data...")
            from comicsdb.models import (
                Arc,
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

            for model in [
                Variant,
                Credits,
                Issue,
                Series,
                SeriesType,
                Imprint,
                Universe,
                Arc,
                Character,
                Creator,
                Team,
                Genre,
                Role,
                Rating,
                Publisher,
            ]:
                model.objects.all().delete()

        self.stdout.write("Seeding development data...")

        # User
        user = UserFactory()

        # Ratings
        ratings = [
            RatingFactory(name="Unknown"),
            RatingFactory(name="Everyone"),
            RatingFactory(name="Teen"),
            RatingFactory(name="Teen Plus"),
            RatingFactory(name="Mature"),
        ]
        self.stdout.write(f"  Created {len(ratings)} ratings")

        # Genres
        genre_names = [
            "Super-Hero",
            "Crime",
            "Horror",
            "Science Fiction",
            "Fantasy",
            "Humor",
            "Romance",
            "Western",
            "War",
            "Mystery",
        ]
        genres = [GenreFactory(name=name) for name in genre_names]
        self.stdout.write(f"  Created {len(genres)} genres")

        # Roles
        role_names = ["Writer", "Artist", "Penciller", "Inker", "Colorist", "Letterer", "Editor"]
        roles = [RoleFactory(name=name, order=i) for i, name in enumerate(role_names)]
        self.stdout.write(f"  Created {len(roles)} roles")

        # Series types
        type_names = [
            "Ongoing Series",
            "Limited Series",
            "Mini-Series",
            "One-Shot",
            "Annual",
            "Graphic Novel",
            "Hardcover",
            "Trade Paperback",
        ]
        series_types = [SeriesTypeFactory(name=name) for name in type_names]
        self.stdout.write(f"  Created {len(series_types)} series types")

        # Publishers
        publishers = [
            PublisherFactory(name="DC Comics", founded=1934, created_by=user, edited_by=user),
            PublisherFactory(name="Marvel", founded=1939, created_by=user, edited_by=user),
            PublisherFactory(name="Image Comics", founded=1992, created_by=user, edited_by=user),
        ]
        self.stdout.write(f"  Created {len(publishers)} publishers")

        # Imprints
        imprints = [
            ImprintFactory(
                name="Vertigo",
                publisher=publishers[0],
                created_by=user,
                edited_by=user,
            ),
            ImprintFactory(
                name="Black Label",
                publisher=publishers[0],
                created_by=user,
                edited_by=user,
            ),
        ]
        self.stdout.write(f"  Created {len(imprints)} imprints")

        # Universes
        universes = [
            UniverseFactory(
                name="Earth-0",
                designation="Prime Earth",
                publisher=publishers[0],
                created_by=user,
                edited_by=user,
            ),
            UniverseFactory(
                name="Earth-616",
                designation="Prime Marvel Universe",
                publisher=publishers[1],
                created_by=user,
                edited_by=user,
            ),
        ]
        self.stdout.write(f"  Created {len(universes)} universes")

        # Arcs
        arcs = ArcFactory.create_batch(5, created_by=user, edited_by=user)
        self.stdout.write(f"  Created {len(arcs)} arcs")

        # Creators
        creators = CreatorFactory.create_batch(10, created_by=user, edited_by=user)
        self.stdout.write(f"  Created {len(creators)} creators")

        # Teams
        teams = TeamFactory.create_batch(5, created_by=user, edited_by=user)
        self.stdout.write(f"  Created {len(teams)} teams")

        # Characters
        characters = CharacterFactory.create_batch(15, created_by=user, edited_by=user)
        self.stdout.write(f"  Created {len(characters)} characters")

        # Series (one per publisher, using the "Ongoing Series" type)
        ongoing_type = series_types[0]
        all_series = []
        for pub in publishers:
            series_batch = SeriesFactory.create_batch(
                3,
                publisher=pub,
                series_type=ongoing_type,
                created_by=user,
                edited_by=user,
            )
            all_series.extend(series_batch)
        self.stdout.write(f"  Created {len(all_series)} series")

        # Add genres to series
        for i, series in enumerate(all_series):
            series.genres.add(genres[i % len(genres)])

        # Issues (5 per series)
        all_issues = []
        for series in all_series:
            for num in range(1, 6):
                issue = IssueFactory(
                    series=series,
                    number=str(num),
                    rating=ratings[num % len(ratings)],
                    created_by=user,
                    edited_by=user,
                )
                issue.characters.add(characters[num % len(characters)])
                issue.teams.add(teams[num % len(teams)])
                issue.universes.add(universes[series.publisher_id % len(universes)])
                if num == 1:
                    issue.arcs.add(arcs[all_series.index(series) % len(arcs)])
                all_issues.append(issue)
        self.stdout.write(f"  Created {len(all_issues)} issues")

        # Credits (assign creators to issues)
        credits_count = 0
        for issue in all_issues:
            for j in range(3):
                creator = creators[(all_issues.index(issue) + j) % len(creators)]
                credit = CreditsFactory(issue=issue, creator=creator)
                credit.role.add(roles[j % len(roles)])
                credits_count += 1
        self.stdout.write(f"  Created {credits_count} credits")

        # Variants (for some issues)
        variants = [VariantFactory(issue=issue) for issue in all_issues[:10]]
        self.stdout.write(f"  Created {len(variants)} variants")

        self.stdout.write(self.style.SUCCESS("Done! Development data seeded successfully."))