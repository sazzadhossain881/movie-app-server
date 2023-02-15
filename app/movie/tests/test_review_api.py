"""Test review for movie api"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Review,
    Movie,
)
from movie.serializers import (
    ReviewSerializer,
    ReviewDetailSerializer,
)

REVIEW_URL = reverse('movie:review-list')


def detail_url(review_id):
    """create and return a review detail url"""
    return reverse('movie:review-detail', args=[review_id])


def create_review(user, **params):
    """create and return a new review"""
    defaults = {
        'rating': 4,
        'description': 'sample description',
        'active': True
    }

    defaults.update(params)

    review = Review.objects.create(user=user, **defaults)
    return review


def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicReviewApiTests(TestCase):
    """Test unauthenticated api request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call api"""
        res = self.client.get(REVIEW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateReviewApiTests(TestCase):
    """Test authenticated api request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com', password='testpass123')
        self.movie = Movie.objects.create(
            title='sample title',
            storyLine='sample storyLine',
            active=True,
            avg_rating=3.00,
            number_rating=4
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_review(self):
        """Test retrieve a list of review"""
        res = self.client.get(REVIEW_URL)
        reviews = Review.objects.all().order_by('-id')
        serializer = ReviewSerializer(reviews, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_review_detail(self):
        review = create_review(user=self.user)
        url = detail_url(review.id)
        res = self.client.get(url)
        serializer = ReviewDetailSerializer(review)
        self.assertEqual(res.data, serializer.data)

    def test_create_review(self):
        """Test creating a review"""
        payload = {
            'rating': 3,
            'description': 'sample review description',
            'active': True
        }

        res = self.client.post(REVIEW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        review = Review.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(review, key), value)
        self.assertEqual(review.user, self.user)

    def test_partial_update(self):
        """Test partial update of a movie"""
        new_rating = 3

        review = create_review(
            user=self.user,
            description='sample review description',
            rating=new_rating,
            active=False

        )

        payload = {
            'description': 'sample review description'
        }

        url = detail_url(review.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.description, payload['description'])
        self.assertEqual(review.rating, new_rating)
        self.assertEqual(review.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the review user result an error"""
        new_user = create_user(email='user2@example.com',
                               password='testpass123')

        review = create_review(user=self.user)
        payload = {
            'user': new_user.id
        }

        url = detail_url(review.id)
        self.client.patch(url, payload)
        review.refresh_from_db()
        self.assertEqual(review.user, self.user)

    def test_delete_movie(self):
        """Test deleting a review is successfull"""
        review = create_review(user=self.user)
        url = detail_url(review.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_other_user_movie_error(self):
        """Test trying to delete other user review gives error"""
        new_user = create_user(email='user2@example.com',
                               password='testpass123')

        review = create_review(user=new_user)
        url = detail_url(review.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(id=review.id).exists())
