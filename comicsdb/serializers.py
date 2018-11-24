from rest_framework import serializers

from comicsdb.models import (Arc, Character, Creator, Credits,
                             Issue, Publisher, Series, Role)


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ('id', 'name')


class CreatorListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Creator
        fields = ('id', 'name')


class CreditsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='creator.id')
    creator = serializers.ReadOnlyField(source='creator.name')
    role = RoleSerializer('role', many=True)

    class Meta:
        model = Credits
        fields = ('id', 'creator', 'role')


class ArcSerializer(serializers.ModelSerializer):

    class Meta:
        model = Arc
        fields = ('id', 'name', 'desc', 'image')


class ArcListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Arc
        fields = ('id', 'name')


class CharacterSerializer(serializers.ModelSerializer):
    creators = CreatorListSerializer(many=True, read_only=True)

    class Meta:
        model = Character
        fields = ('id', 'name', 'alias', 'desc', 'image', 'creators')


class CharacterListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Character
        fields = ('id', 'name')


class IssueSerializer(serializers.ModelSerializer):
    credits = CreditsSerializer(
        source='credits_set', many=True, read_only=True)
    arcs = ArcListSerializer(many=True, read_only=True)
    characters = CharacterListSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = ('id', '__str__', 'name', 'number', 'cover_date',
                  'store_date', 'desc', 'arcs', 'image', 'credits', 'characters')


class PublisherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Publisher
        fields = ('id', 'name', 'founded', 'desc', 'image')


class SeriesImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True,
                                   allow_null=True, required=False)

    class Meta:
        model = Issue
        fields = ('image',)


class SeriesSerializer(serializers.ModelSerializer):
    issue_count = serializers.ReadOnlyField
    image = SeriesImageSerializer(source='issue_set.first', many=False)
    series_type = serializers.ReadOnlyField(source='series_type.name')

    class Meta:
        model = Series
        fields = ('id', 'name', 'sort_name', 'volume', 'series_type',
                  'year_began', 'year_end', 'desc', 'issue_count', 'image')

    def to_representation(self, obj):
        """ Move image field from Issue to Series representation. """
        representation = super().to_representation(obj)
        issue_representation = representation.pop('image')
        for key in issue_representation:
            representation[key] = issue_representation[key]

        return representation
