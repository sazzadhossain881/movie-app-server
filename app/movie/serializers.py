from rest_framework import serializers
from core.models import (
    Stream,
    Movie,
    Review,
)


class ReviewSerializer(serializers.ModelSerializer):
    """serializer for review"""
    class Meta:
        model = Review
        fields = ['id', 'rating',
                  'active', 'created', 'update', 'description']


class ReviewDetailSerializer(ReviewSerializer):
    """serializer for review detail"""
    user = serializers.StringRelatedField(read_only=True)

    class Meta(ReviewSerializer.Meta):
        fields = ReviewSerializer.Meta.fields+['user', 'movie']


class MovieSerializer(serializers.ModelSerializer):
    """serializer for movies"""

    class Meta:
        model = Movie
        fields = ['id', 'title', 'image', 'platform', 'active',
                  'avg_rating', 'number_rating', 'created']
        read_only_fields = ['id']


class StreamSerializer(serializers.ModelSerializer):
    """serializer for stream"""
    movies = MovieSerializer(many=True, read_only=True)

    class Meta:
        model = Stream
        fields = ['id', 'name', 'about', 'website', 'movies']
        read_only_fields = ['id']


class MovieDetailSerializer(MovieSerializer):
    """serializer for movie detail view"""
    review = ReviewDetailSerializer(many=True, read_only=True)

    class Meta(MovieSerializer.Meta):
        fields = MovieSerializer.Meta.fields+['storyLine', 'review']


class MovieImageSerializer(serializers.ModelSerializer):
    """serializer for uploading image to movie"""
    class Meta:
        model = Movie
        fields = ['id', 'image']
        read_only_field = ['id']
        extra_kwargs = {
            'image': {
                'required': 'True'
            }
        }
