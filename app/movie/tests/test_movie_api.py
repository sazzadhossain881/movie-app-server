"""Test for the movie api"""

import tempfile
import os
from PIL import Image
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Movie,
    Stream,
)
from movie.serializers import (
    MovieSerializer,
    MovieDetailSerializer,
)


MOVIE_URL = reverse('movie:movie-list')


def detail_url(movie_id):
    """create and return a movie detail url"""
    return reverse('movie:movie-detail', args=[movie_id])


def image_upload_url(movie_id):
    """create and return image upload url"""
    return reverse('movie:movie-upload-image', args=[movie_id])


def create_movie(user, **params):
    """create and return a sample movie"""
    defaults = {
        'title': 'sample title',
        'storyLine': 'sample storyLine',
        'active': True,
        'avg_rating': Decimal('3.30'),
        'number_rating': 4
    }

    defaults.update(params)
    movie = Movie.objects.create(user=user, **defaults)
    return movie


def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicMovieApiTests(TestCase):
    """Test unauthenticated api request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call api"""
        res = self.client.get(MOVIE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMovieApiTests(TestCase):
    """Test authenticated api request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com', password='testpass123')
        self.platform = Stream.objects.create(
            name='Netflix',
            about='samle about',
            website='http://www.netflix.com'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_movies(self):
        """Test retrieve a list of movies"""

        # create_movie(user=self.user)
        # create_movie(user=self.user)

        res = self.client.get(MOVIE_URL)
        movies = Movie.objects.all().order_by('-id')
        serializer = MovieSerializer(movies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # def test_movie_list_limited_to_user(self):
    #     """Test list of movie is limited to user"""
    #     other_user = create_user(
    #         email='other@example.com', password='testpass123')

    #     create_movie(user=other_user)
    #     create_movie(user=self.user)

    #     res = self.client.get(MOVIE_URL)
    #     movies = Movie.objects.filter(user=self.user)
    #     serializer = MovieSerializer(movies, many=True)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(res.data, serializer.data)

    def test_get_movie_detail(self):
        movie = create_movie(user=self.user, platform=self.platform)
        url = detail_url(movie.id)
        res = self.client.get(url)
        serializer = MovieDetailSerializer(movie)
        self.assertEqual(res.data, serializer.data)

    def test_create_movie(self):
        """Test creating a movie"""
        payload = {
            'title': 'sample title',
            'storyLine': 'sample storyLine of netflix',
            'active': True
        }

        res = self.client.post(MOVIE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update(self):
        """Test partial update of a movie"""
        new_storyLine = 'sample new storyLine'

        movie = create_movie(
            user=self.user,
            title='sample movie title',
            storyLine=new_storyLine,
            active=False

        )

        payload = {
            'title': 'sample movie title'
        }

        url = detail_url(movie.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        movie.refresh_from_db()
        self.assertEqual(movie.title, payload['title'])
        self.assertEqual(movie.storyLine, new_storyLine)
        self.assertEqual(movie.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the movie user result an error"""
        new_user = create_user(email='user2@example.com',
                               password='testpass123')

        movie = create_movie(user=self.user)
        payload = {
            'user': new_user.id
        }

        url = detail_url(movie.id)
        self.client.patch(url, payload)
        movie.refresh_from_db()
        self.assertEqual(movie.user, self.user)

    def test_delete_movie(self):
        """Test deleting a movie is successfull"""
        movie = create_movie(user=self.user)
        url = detail_url(movie.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Movie.objects.filter(id=movie.id).exists())

    def test_other_user_movie_error(self):
        """Test trying to delete other user movie gives error"""
        new_user = create_user(email='user2@example.com',
                               password='testpass123')

        movie = create_movie(user=new_user)
        url = detail_url(movie.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Movie.objects.filter(id=movie.id).exists())


class ImageUploadTest(TestCase):
    """Test for the image upload api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123'
        )
        self.client.force_authenticate(self.user)
        self.movie = create_movie(user=self.user)

    def tearDown(self):
        self.movie.image.delete()

    def test_upload_image(self):
        """Test upload image to a recipe"""
        url = image_upload_url(self.movie.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.movie.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.movie.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image"""
        url = image_upload_url(self.movie.id)
        payload = {'image': 'not an image'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
