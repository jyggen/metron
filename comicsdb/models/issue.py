import itertools
import logging

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import pre_save
from django.urls import reverse
from django.utils.text import slugify
from sorl.thumbnail import ImageField

from users.models import CustomUser

from .arc import Arc
from .attribution import Attribution
from .character import Character
from .common import CommonInfo
from .creator import Creator
from .series import Series
from .team import Team

LOGGER = logging.getLogger(__name__)


class GraphicNovelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(series__series_type__name="Graphic Novel")


class Issue(CommonInfo):
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    name = ArrayField(models.CharField("Story Title", max_length=150), null=True, blank=True)
    number = models.CharField(max_length=25)
    arcs = models.ManyToManyField(Arc, blank=True)
    cover_date = models.DateField("Cover Date")
    store_date = models.DateField("In Store Date", null=True, blank=True)
    price = models.DecimalField(
        "Cover Price", max_digits=5, decimal_places=2, null=True, blank=True
    )
    sku = models.CharField("Distributor SKU", max_length=9, blank=True)
    upc = models.CharField("UPC Code", max_length=20, blank=True)
    page = models.PositiveSmallIntegerField("Page Count", null=True, blank=True)
    image = ImageField("Cover", upload_to="issue/%Y/%m/%d/", blank=True)
    creators = models.ManyToManyField(Creator, through="Credits", blank=True)
    characters = models.ManyToManyField(Character, blank=True)
    teams = models.ManyToManyField(Team, blank=True)
    reprints = models.ManyToManyField("self", blank=True)
    attribution = GenericRelation(Attribution, related_query_name="issues")
    created_by = models.ForeignKey(CustomUser, default=1, on_delete=models.SET_DEFAULT)
    edited_by = models.ForeignKey(
        CustomUser, default=1, on_delete=models.SET_DEFAULT, related_name="editor"
    )

    objects = models.Manager()
    graphic_novels = GraphicNovelManager()

    def get_absolute_url(self):
        return reverse("issue:detail", args=[self.slug])

    @property
    def wikipedia(self):
        return self.attribution.filter(source=Attribution.Source.WIKIPEDIA)

    @property
    def marvel(self):
        return self.attribution.filter(source=Attribution.Source.MARVEL)

    def save(self, *args, **kwargs) -> None:
        # Let's delete the original image if we're replacing it by uploading a new one.
        try:
            this = Issue.objects.get(id=self.id)
            if this.image and this.image != self.image:
                LOGGER.info(
                    f"Replacing {this.image} with {'None' if not(img:=self.image) else img}."
                )
                this.image.delete(save=False)
        except ObjectDoesNotExist:
            pass
        return super(Issue, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.series.name} #{self.number}"

    class Meta:
        unique_together = ["series", "number"]
        ordering = ["series__sort_name", "cover_date", "store_date", "number"]


def generate_issue_slug(issue):
    slug_candidate = slug_original = slugify(f"{issue.series.slug}-{issue.number}")
    for i in itertools.count(1):
        if not Issue.objects.filter(slug=slug_candidate).exists():
            break
        slug_candidate = f"{slug_original}-{i}"

    return slug_candidate


def pre_save_issue_slug(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = generate_issue_slug(instance)


pre_save.connect(pre_save_issue_slug, sender=Issue)
