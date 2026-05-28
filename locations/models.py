from unidecode import unidecode
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.utils.text import slugify
from .choices import RATING_CHOICES, VOTE_CHOICES


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name), allow_unicode=True)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=16, decimal_places=14)
    longitude = models.DecimalField(max_digits=16, decimal_places=14)
    popularity_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_popularity(self):
        """
        Formula: Average rating * (Number of reviews + 1)
        """
        stats = self.reviews.aggregate(
            avg_rating=Avg('rating'),
            count=Count('id')
        )
        avg_rating = stats['avg_rating'] or 0
        count = stats['count'] or 0
        self.popularity_score = float(avg_rating * (count + 1))
        self.save()

    def __str__(self):
        return self.name

class Review(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.location.name}"

class ReviewVote(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_votes')
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('review', 'user')

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'location')
