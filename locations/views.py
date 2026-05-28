from http import HTTPMethod

import pandas as pd
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from custom_view import CustomModelViewSet
from .models import Category, Location, Review, ReviewVote, Subscription, PasswordReset
from .serializers import (
    UserSerializer,
    CategorySerializer,
    LocationSerializer,
    ReviewSerializer,
    SubscriptionSerializer,
    ResetPasswordRequestSerializer,
    ResetPasswordSerializer,
)


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class RequestPasswordResetView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        user = User.objects.filter(email=email).first()

        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset = PasswordReset(email=email, token=token)
            reset.save()

            reset_url = request.build_absolute_uri(
                reverse("reset_password_confirm", kwargs={"token": token})
            )

            print(reset_url)

            if user.email:
                html_message = render_to_string(
                    "locations/emails/password_reset.html", {"reset_url": reset_url}
                )
                send_mail(
                    subject="Password reset",
                    message=f"Відновлення паролю: {reset_url}",
                    from_email=None,
                    recipient_list=[user.email],
                    fail_silently=True,
                    html_message=html_message,
                )
            else:
                return Response(
                    {"message": "User does not have an email address."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"message": "Password reset email sent."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, token):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        new_password = data["new_password"]
        confirm_password = data["confirm_password"]

        if new_password != confirm_password:
            return Response(
                {"message": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reset_obj = PasswordReset.objects.filter(token=token).first()

        if not reset_obj:
            return Response(
                {"message": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=reset_obj.email).first()

        if user:
            user.set_password(new_password)
            user.save()
            reset_obj.delete()
            return Response(
                {"message": "Password reset successfully."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )


class CategoryViewSet(CustomModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    list_cache_key = "category_list"
    retrieve_cache_key = "category_detail"


class LocationViewSet(CustomModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "popularity_score"]
    search_fields = ["name", "description"]
    ordering_fields = ["popularity_score", "created_at"]
    list_cache_key = "location_list"
    retrieve_cache_key = "location_detail"

    @action(detail=False, methods=[HTTPMethod.GET])
    def export(self, request):
        export_format = request.query_params.get("format", "csv").lower()
        locations = Location.objects.all().values(
            "id",
            "name",
            "description",
            "category__name",
            "latitude",
            "longitude",
            "popularity_score",
        )
        df = pd.DataFrame(list(locations))

        if export_format == "json":
            content = df.to_json(orient="records")
            response = HttpResponse(content, content_type="application/json")
            response["Content-Disposition"] = 'attachment; filename="locations.json"'
            return response
        else:
            content = df.to_csv(index=False)
            response = HttpResponse(content, content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="locations.csv"'
            return response

    @action(
        detail=True,
        methods=[HTTPMethod.POST],
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, pk=None):
        location = self.get_object()
        subscription, created = Subscription.objects.get_or_create(
            user=request.user, location=location
        )
        if created:
            return Response({"status": "subscribed"}, status=status.HTTP_201_CREATED)
        return Response({"status": "already subscribed"}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=[HTTPMethod.POST],
        permission_classes=[permissions.IsAuthenticated],
    )
    def unsubscribe(self, request, pk=None):
        location = self.get_object()
        Subscription.objects.filter(user=request.user, location=location).delete()
        return Response({"status": "unsubscribed"}, status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(CustomModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    list_cache_key = "review_list"
    retrieve_cache_key = "review_detail"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=True,
        methods=[HTTPMethod.POST],
        permission_classes=[permissions.IsAuthenticated],
    )
    def vote(self, request, pk=None):
        review = self.get_object()
        vote_value = request.data.get("vote")

        if vote_value not in [1, -1]:
            return Response(
                {"error": "Invalid vote value. Use 1 for Like and -1 for Dislike."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vote, _ = ReviewVote.objects.update_or_create(
            review=review, user=request.user, defaults={"vote": vote_value}
        )
        return Response({"status": "vote recorded"}, status=status.HTTP_200_OK)


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
