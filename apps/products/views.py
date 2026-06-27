"""API views for product and category CRUD operations.

Uses ``api_response`` wrapper for consistent ``{success, data}`` format
across all endpoints. Supports filtering, searching, and ordering via
django-filter and DRF backends.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.core.mixins import APIResponseMixin
from apps.core.response import api_response
from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
)
from .permissions import IsProductOwnerOrReadOnly, IsStaffForCategories
from .filters import ProductFilter


class CategoryListCreateView(generics.ListCreateAPIView):
    """List all categories or create a new one.

    **Permissions:**
      - ``GET`` — any visitor (no authentication required)
      - ``POST`` — **superuser (staff) only**
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffForCategories]
    pagination_class = None

    def list(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return api_response(success=True, data=serializer.data)

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(success=True, data=serializer.data, status_code=status.HTTP_201_CREATED)


class CategoryDetailView(APIResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a category.

    **Permissions:**
      - ``GET`` — any visitor (no authentication required)
      - ``PUT``, ``PATCH``, ``DELETE`` — **superuser (staff) only**
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffForCategories]
    destroy_message = "Category deleted"

    def retrieve(self, request, *args, **kwargs) -> Response:
        return api_response(success=True, data=self.get_serializer(self.get_object()).data)


class ProductListCreateView(generics.ListCreateAPIView):
    """List all products (with filters/search/ordering) or create a new one.

    Uses ``ProductListSerializer`` for reads and ``ProductDetailSerializer``
    for writes.

    **Permissions:**
      - ``GET`` — any visitor (filters: search by name/description, order by name/price/created_at)
      - ``POST`` — **authenticated user** (auto-assigned as owner)

    **Fields for creation (POST):**

      - ``name`` (string, required) — unique product name
      - ``price`` (decimal, required) — must be greater than 0
      - ``description`` (string, optional)
      - ``category_id`` (integer, optional) — ID of an existing category
      - ``is_active`` (boolean, optional, default: true)
    """

    queryset = Product.objects.select_related("category", "created_by")
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductDetailSerializer
        return ProductListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(success=True, data=serializer.data, status_code=status.HTTP_201_CREATED)

    def get_paginated_response(self, data):
        return api_response(success=True, data=data)

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return api_response(success=True, data=serializer.data)


class ProductDetailView(APIResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a product.

    **Permissions:**
      - ``GET`` — any visitor
      - ``PUT``, ``PATCH``, ``DELETE`` — **product owner or superuser (staff)** only
    """

    queryset = Product.objects.select_related("category", "created_by")
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsProductOwnerOrReadOnly]
    destroy_message = "Product deleted"

    def retrieve(self, request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(success=True, data=serializer.data)
