from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Location, Review, ReviewVote, Subscription

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Location
        fields = (
            'id', 'name', 'description', 'category', 'category_name',
            'latitude', 'longitude', 'popularity_score', 'created_at', 'updated_at'
        )
        read_only_fields = ('popularity_score',)

class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            'id', 'location', 'user', 'user_username', 'text', 
            'rating', 'likes_count', 'dislikes_count', 'created_at'
        )
        read_only_fields = ('user',)

    def get_likes_count(self, obj):
        return obj.votes.filter(vote=1).count()

    def get_dislikes_count(self, obj):
        return obj.votes.filter(vote=-1).count()

class ReviewVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewVote
        fields = ('id', 'review', 'user', 'vote')
        read_only_fields = ('user',)

class SubscriptionSerializer(serializers.ModelSerializer):
    location_name = serializers.ReadOnlyField(source='location.name')

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'location', 'location_name', 'created_at')
        read_only_fields = ('user',)
