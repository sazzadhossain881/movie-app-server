"""url mapping for the movie api"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from movie import views

router = DefaultRouter()
router.register('streams', views.StreamViewSet)
router.register('movies', views.MovieViewSet)

app_name = 'movie'

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/review-create/',
         views.ReviewCreate.as_view(), name='review-create'),
    path('<int:pk>/reviews/', views.ReviewList.as_view(), name='review-list'),
    path('review/<int:pk>/', views.ReviewDetail.as_view(), name='review-detail'),
    path('reviews/', views.UserReview.as_view(), name='user-review-detail'),

]
