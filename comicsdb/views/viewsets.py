from django.db.models import Prefetch
from django.http import Http404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.throttling import UserRateThrottle

from comicsdb.filters.issue import IssueFilter
from comicsdb.filters.name import NameFilter
from comicsdb.filters.series import SeriesFilter
from comicsdb.models import (
    Arc,
    Character,
    Creator,
    Credits,
    Issue,
    Publisher,
    Role,
    Series,
    Team,
)
from comicsdb.models.series import SeriesType
from comicsdb.serializers import (
    ArcListSerializer,
    ArcSerializer,
    CharacterListSerializer,
    CharacterSerializer,
    CreatorListSerializer,
    CreatorSerializer,
    IssueListSerializer,
    IssueSerializer,
    PublisherListSerializer,
    PublisherSerializer,
    RoleSerializer,
    SeriesListSerializer,
    SeriesReadSerializer,
    SeriesSerializer,
    SeriesTypeSerializer,
    TeamListSerializer,
    TeamSerializer,
)


class ArcViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    Returns a list of all the story arcs.

    retrieve:
    Returns the information of an individual story arc.
    """

    queryset = Arc.objects.all()
    filterset_class = NameFilter
    throttle_classes = (UserRateThrottle,)

    def get_serializer_class(self):
        match self.action:
            case "list":
                return ArcListSerializer
            case "issue_list":
                return IssueListSerializer
            case _:
                return ArcSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsAdminUser]
        elif self.action in ["retrieve", "list", "series_list"]:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer: ArcSerializer) -> None:
        serializer.save(edited_by=self.request.user)
        return super().perform_create(serializer)

    def perform_update(self, serializer: ArcSerializer) -> None:
        serializer.save(edited_by=self.request.user)
        return super().perform_update(serializer)

    @action(detail=True)
    def issue_list(self, request, pk=None):
        """
        Returns a list of issues for a story arc.
        """
        arc = self.get_object()
        queryset = arc.issue_set.select_related("series", "series__series_type").order_by(
            "cover_date", "series", "number"
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = IssueListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        else:
            raise Http404()


class CharacterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Return a list of all the characters.

    retrieve:
    Returns the information of an individual character.
    """

    queryset = Character.objects.all()
    filterset_class = NameFilter
    throttle_classes = (UserRateThrottle,)

    def get_serializer_class(self):
        match self.action:
            case "retrieve":
                return CharacterSerializer
            case _:
                return CharacterListSerializer

    @action(detail=True)
    def issue_list(self, request, pk=None):
        """
        Returns a list of issues for a character.
        """
        character = self.get_object()
        queryset = character.issue_set.select_related(
            "series", "series__series_type"
        ).order_by("cover_date", "series", "number")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = IssueListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        else:
            raise Http404()


class CreatorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Return a list of all the creators.

    retrieve:
    Returns the information of an individual creator.
    """

    queryset = Creator.objects.all()
    filterset_class = NameFilter
    throttle_classes = (UserRateThrottle,)

    def get_serializer_class(self):
        match self.action:
            case "retrieve":
                return CreatorSerializer
            case _:
                return CreatorListSerializer


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:
    Return a list of all the issues.

    retrieve:
    Returns the information of an individual issue.
    """

    queryset = Issue.objects.select_related(
        "series", "series__series_type", "rating"
    ).prefetch_related(
        Prefetch(
            "credits_set",
            queryset=Credits.objects.order_by("creator__name")
            .distinct("creator__name")
            .select_related("creator")
            .prefetch_related("role"),
        ),
        Prefetch(
            "reprints",
            queryset=Issue.objects.select_related("series", "series__series_type"),
        ),
    )
    filterset_class = IssueFilter
    throttle_classes = (UserRateThrottle,)

    def get_serializer_class(self):
        match self.action:
            case "retrieve":
                return IssueSerializer
            case _:
                return IssueListSerializer


class PublisherViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    Returns a list of all publishers.

    retrieve:
    Returns the information of an individual publisher.

    create:
    Add a new publisher.

    update:
    Update a publisher's information.
    """

    queryset = Publisher.objects.prefetch_related("series_set")
    filterset_class = NameFilter
    throttle_classes = (UserRateThrottle,)

    def get_serializer_class(self):
        match self.action:
            case "list":
                return PublisherListSerializer
            case "series_list":
                return SeriesListSerializer
            case _:
                return PublisherSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsAdminUser]
        elif self.action in ["retrieve", "list", "series_list"]:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer: PublisherSerializer) -> None:
        serializer.save(edited_by=self.request.user)
        return super().perform_create(serializer)

    def perform_update(self, serializer: PublisherSerializer) -> None:
        serializer.save(edited_by=self.request.user)
        return super().perform_update(serializer)

    @action(detail=True)
    def series_list(self, request, pk=None):
        """
        Returns a list of series for a publisher.
        """
        publisher = self.get_object()
        queryset = publisher.series_set.select_related("series_type").prefetch_related(
            "issue_set"
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SeriesListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        else:
            raise Http404()


class RoleViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
    Returns a list of all the creator roles.
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filterset_class = NameFilter
    throttle_classes = (UserRateThrottle,)


class SeriesViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    Returns a list of all the comic series.

    retrieve:
    Returns the information of an individual comic series.

    create:
    Add a new Series.

    update:
    Update a Series information.
    """

    queryset = Series.objects.select_related("series_type", "publisher")
    serializer_class = SeriesSerializer
    filterset_class = SeriesFilter
    throttle_classes = (UserRateThrottle,)

    def get_serializer_class(self):
        match self.action:
            case "list":
                return SeriesListSerializer
            case "issue_list":
                return IssueListSerializer
            case "retrieve":
                return SeriesReadSerializer
            case _:
                return SeriesSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsAdminUser]
        elif self.action in ["retrieve", "list", "series_list"]:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer: SeriesSerializer) -> None:
        serializer.save(edited_by=self.request.user)
        return super().perform_create(serializer)

    def perform_update(self, serializer: SeriesSerializer) -> None:
        serializer.save(edited_by=self.request.user)
        return super().perform_update(serializer)

    @action(detail=True)
    def issue_list(self, request, pk=None):
        """
        Returns a list of issues for a series.
        """
        series = self.get_object()
        queryset = series.issue_set.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = IssueListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        else:
            raise Http404()


class SeriesTypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
    Returns a list of the Series Types available.
    """

    queryset = SeriesType.objects.all()
    serializer_class = SeriesTypeSerializer
    filterset_class = NameFilter
    throttle_classes = (UserRateThrottle,)


class TeamViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    list:
    Return a list of all the teams.

    retrieve:
    Returns the information of an individual team.
    """

    queryset = Team.objects.all()
    filterset_class = NameFilter
    throttle_classes = (UserRateThrottle,)

    def get_serializer_class(self):
        match self.action:
            case "list":
                return TeamListSerializer
            case "issue_list":
                return IssueListSerializer
            case _:
                return TeamSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ["create", "update", "partial_update"]:
            permission_classes = [IsAdminUser]
        elif self.action in ["retrieve", "list", "series_list"]:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer: TeamSerializer) -> None:
        serializer.save(edited_by=self.request.user)
        return super().perform_create(serializer)

    def perform_update(self, serializer: TeamSerializer) -> None:
        serializer.save(edited_by=self.request.user)
        return super().perform_update(serializer)

    @action(detail=True)
    def issue_list(self, request, pk=None):
        """
        Returns a list of issues for a character.
        """
        team = self.get_object()
        queryset = team.issue_set.select_related("series", "series__series_type").order_by(
            "cover_date", "series", "number"
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = IssueListSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        else:
            raise Http404()
