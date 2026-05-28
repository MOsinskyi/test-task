from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView, CategoryViewSet, LocationViewSet,
    ReviewViewSet, SubscriptionViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('auth/', include('rest_framework.urls')),
]
