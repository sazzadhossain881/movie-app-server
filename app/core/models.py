"""Database models"""
import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager

from django.core.validators import MinValueValidator, MaxValueValidator

from django.conf import settings


def movie_image_file_path(instance, filename):
    """Generate file path for new dessert image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'movie', filename)


class UserProfileManager(BaseUserManager):
    """manager for the user profile"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('user must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """user in the system"""
    email = models.EmailField(max_length=250, unique=True)
    name = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()
    USERNAME_FIELD = 'email'


class Stream(models.Model):
    """stream objects"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=250)
    about = models.CharField(max_length=250)
    website = models.URLField(max_length=250)

    def __str__(self):
        return self.name


class Movie(models.Model):
    """movie objects"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=250)
    image = models.ImageField(null=True, upload_to=movie_image_file_path)
    storyLine = models.CharField(max_length=250)
    platform = models.ForeignKey(
        Stream,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="movies"
    )
    active = models.BooleanField(default=True)
    avg_rating = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0)
    number_rating = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    """Review objects"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.CharField(max_length=250, null=True)
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="review",
    )
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.rating) + " | " + self.movie.title + " | " + str(self.user)
