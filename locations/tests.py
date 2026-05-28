import pytest
from django.contrib.auth.models import User
from locations.models import Category, Location, Review, Subscription
from django.conf import settings


@pytest.mark.django_db
def test_popularity_calculation():
    category = Category.objects.create(name="Test Category", slug="test-cat")
    location = Location.objects.create(
        name="Test Location",
        description="A test location",
        category=category,
        latitude=10.0,
        longitude=10.0,
    )

    user = User.objects.create_user(
        username=getattr(settings, "TEST_USER1_USERNAME"),
        password=getattr(settings, "TEST_USER1_PASSWORD"),
    )

    assert location.popularity_score == 0.0

    Review.objects.create(location=location, user=user, text="Great place!", rating=5)

    location.refresh_from_db()

    assert location.popularity_score == 10.0

    Review.objects.create(location=location, user=user, text="Not bad", rating=3)

    location.refresh_from_db()
    # Avg rating: (5 + 3) / 2 = 4.0
    # Count: 2
    # Popularity: 4.0 * (2 + 1) = 12.0
    assert location.popularity_score == 12.0


@pytest.mark.django_db
def test_subscription_signal(mailoutbox):
    category = Category.objects.create(name="Test Category", slug="test-cat")
    location = Location.objects.create(
        name="Test Location",
        description="A test location",
        category=category,
        latitude=10.0,
        longitude=10.0,
    )

    user1 = User.objects.create_user(
        username=getattr(settings, "TEST_USER1_USERNAME"),
        email=getattr(settings, "TEST_USER1_EMAIL"),
        password=getattr(settings, "TEST_USER1_PASSWORD"),
    )
    user2 = User.objects.create_user(
        username=getattr(settings, "TEST_USER2_USERNAME"),
        email=getattr(settings, "TEST_USER2_EMAIL"),
        password=getattr(settings, "TEST_USER2_PASSWORD"),
    )

    Subscription.objects.create(user=user1, location=location)

    Review.objects.create(
        location=location, user=user2, text="Check this out!", rating=4
    )

    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == f"New review for {location.name}"
    assert "user1@example.com" in mailoutbox[0].to
