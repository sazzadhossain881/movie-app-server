"""Test for models"""

from unittest.mock import patch
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_sucessfull(self):
        """Test creating a with with email is successfull"""
        email = 'test@example.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new user"""
        sample_emails = [
            ['test1@Example.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email,
                'sample123'
            )

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without email raises valueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                '', 'testpass123'
            )

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'testpass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_stream(self):
        """Test creating a stream is successfull"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )

        stream = models.Stream.objects.create(
            user=user,
            name='sample name',
            about='sample about',
            website='http://www.netflix.com'
        )

        self.assertEqual(str(stream), stream.name)

    def test_create_movie(self):
        """Test creating a movie is successfull"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        platform = models.Stream.objects.create(
            name='Netflix',
            about='sample about',
            website='http://www.netflix.com'
        )
        movies = models.Movie.objects.create(
            user=user,
            title='sample title',
            storyLine='sample storyLine',
            platform=platform,
            active=True,
            avg_rating=Decimal('4.50'),
            number_rating=4
        )

        self.assertEqual(str(movies), movies.title)

    def test_create_review(self):
        # Test creating a review is successfull
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )

        platform = models.Stream.objects.create(
            name='Netflix',
            about='sample about',
            website='http://www.netflix.com'
        )
        movie = models.Movie.objects.create(
            user=user,
            title='sample title',
            storyLine='sample storyLine',
            platform=platform,
            active=True,
            avg_rating=Decimal('4.50'),
            number_rating=4
        )

        review = models.Review.objects.create(
            user=user,
            movie=movie,
            rating=4,
            description='sample description',
            active=True
        )

        self.assertEqual(str(review), str(
            review.rating)+" | "+str(review.movie)+" | "+str(review.user))

    @patch('core.models.uuid.uuid4')
    def test_movie_file_name_uuid(self, mock_uuid):
        """Test generating image path"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.movie_image_file_path(None, 'exmaple.jpg')
        self.assertEqual(file_path, f'uploads/movie/{uuid}.jpg')
