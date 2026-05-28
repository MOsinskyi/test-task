from typing import Optional

from django.core.cache import cache
from django.views.decorators.cache import cache_page
from rest_framework import viewsets


class CustomModelViewSet(viewsets.ModelViewSet):
    list_cache_key: Optional[str] = None
    retrieve_cache_key: Optional[str] = None
    list_cache_timeout: int = 60 * 15
    retrieve_cache_timeout: int = 60 * 2

    def list(self, request, *args, **kwargs):
        if self.list_cache_key:
            return cache_page(self.list_cache_timeout, key_prefix=self.list_cache_key)(
                super().list
            )(request, *args, **kwargs)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if self.retrieve_cache_key:
            return cache_page(self.retrieve_cache_timeout, key_prefix=self.retrieve_cache_key)(
                super().retrieve
            )(request, *args, **kwargs)
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.clear()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        cache.clear()
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        cache.clear()
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        cache.clear()
        return response
