"""Test fot the stream api"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Stream,
)

from movie.serializers import StreamSerializer


STREAM_URL = reverse('movie:stream-list')


def create_stream(**params):
    """create and return a new stream"""
    defaults = {
        'name': 'sample title',
        'about': 'sample about',
        'website': 'http://www.netflix.com'
    }

    defaults.update(params)
    stream = Stream.objects.create(**defaults)
    return stream


def detail_url(stream_id):
    """create and return a stream detail url"""
    return reverse('movie:stream-detail', args=[stream_id])


def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicStreamApiTests(TestCase):
    """Test unauthenticated api request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_requires(self):
        """Test auth is required for retrieve stream"""
        res = self.client.get(STREAM_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateStreamApiTests(TestCase):
    """Test authenticated api request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com', password='testpass123')

        self.client.force_authenticate(self.user)

    def test_retrieve_stream(self):
        """Test retrieving a list of stream"""
        res = self.client.get(STREAM_URL)
        stream = Stream.objects.all().order_by('-name')
        serializer = StreamSerializer(stream, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_stream(self):
        """Test creating a stream"""
        payload = {
            'name': 'sample stream name',
            'about': 'sample movie about',
            'website': 'http://www.netflix.com'
        }

        res = self.client.post(STREAM_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_stream(self):
        """Test updating a stream"""
        new_website = 'http://www.primevideo.com'

        stream = create_stream(

            name='sample stream name',
            website=new_website
        )

        payload = {
            'name': 'sample stream name'
        }

        url = detail_url(stream.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        stream.refresh_from_db()
        self.assertEqual(stream.name, payload['name'])
        self.assertEqual(stream.website, new_website)

    def test_full_update(self):
        """Test full update of stream"""
        stream = create_stream(
            user=self.user,
            name='sample stream name',
            about='sample stream about',
            website='http://www.netflix.com'
        )

        payload = {
            'name': 'sample stream name',
            'about': 'sample stream about',
            'website': 'http://www.netflix.com'
        }

        url = detail_url(stream.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        stream.refresh_from_db()

        for key, value in payload.items():
            self.assertEqual(getattr(stream, key), value)
        self.assertEqual(stream.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the movie user result an error"""
        new_user = create_user(email='user2@example.com',
                               password='testpass123')

        stream = create_stream(user=self.user)
        payload = {
            'user': new_user.id
        }

        url = detail_url(stream.id)
        self.client.patch(url, payload)
        stream.refresh_from_db()
        self.assertEqual(stream.user, self.user)

    def test_delete_stream(self):
        """Test deleting a movie is successfull"""
        stream = create_stream(user=self.user)
        url = detail_url(stream.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Stream.objects.filter(id=stream.id).exists())

    def test_other_user_stream_error(self):
        """Test trying to delete other user movie gives error"""
        new_user = create_user(email='user2@example.com',
                               password='testpass123')

        stream = create_stream(user=new_user)
        url = detail_url(stream.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Stream.objects.filter(id=stream.id).exists())
