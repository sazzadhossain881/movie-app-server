"""views for the movie api"""
from rest_framework import mixins, viewsets, generics
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import (
    Stream,
    Movie,
    Review,
)
from movie.serializers import (
    StreamSerializer,
    MovieSerializer,
    MovieDetailSerializer,
    ReviewSerializer,
    ReviewDetailSerializer,
    MovieImageSerializer,
)
from movie import permissions

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404


class StreamViewSet(
    viewsets.ModelViewSet
):
    """manage stream in the database"""
    serializer_class = StreamSerializer
    queryset = Stream.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [
        IsAuthenticated,
        permissions.IsAdminOrReadOnly
    ]

    def get_queryset(self):
        """filter queryset to authenticated user"""
        return Stream.objects.all().order_by('-name')

    def perform_create(self, serializer):
        """create a new stream"""
        serializer.save(user=self.request.user)


class MovieViewSet(viewsets.ModelViewSet):
    """view for manage movie api"""
    serializer_class = MovieDetailSerializer
    queryset = Movie.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [
        IsAuthenticated,
        permissions.IsAdminOrReadOnly
    ]

    def get_queryset(self):
        """retrieve movie for authenticated user"""
        return Movie.objects.all().order_by('-id')

    def get_serializer_class(self):
        """return the serializer for request"""
        if self.action == 'list':
            return MovieSerializer
        elif self.action == 'upload_image':
            return MovieImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """create a new movie"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """upload an image to dessert"""
        movie = self.get_object()
        serializer = self.get_serializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserReview(generics.ListAPIView):
    serializer_class = ReviewDetailSerializer
    queryset = Review.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [
        IsAuthenticated,
        permissions.IsReviewUserOrReadOnly
    ]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        movie = Movie.objects.get(pk=pk)

        user = self.request.user
        review_queryset = Review.objects.filter(
            movie=movie, user=user)

        if review_queryset.exists():
            raise ValidationError("You have already reviewed this movie!")

        if movie.number_rating == 0:
            movie.avg_rating = serializer.validated_data['rating']
        else:
            movie.avg_rating = (
                movie.avg_rating + serializer.validated_data['rating'])/2

        movie.number_rating = movie.number_rating + 1
        movie.save()

        serializer.save(movie=movie, user=user)


class ReviewList(generics.ListAPIView):
    serializer_class = ReviewDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [
        IsAuthenticated,
        permissions.IsReviewUserOrReadOnly
    ]

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(movie=pk)


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewDetailSerializer
    queryset = Review.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [
        IsAuthenticated,
        permissions.IsReviewUserOrReadOnly
    ]

    def get_queryset(self):
        """retrieve review for authenticated user"""
        return Review.objects.all()
