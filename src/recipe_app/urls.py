from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipe_app import views

router = DefaultRouter()
router.register('tags', views.TagViewSet)
app_name = 'recipe_app'

urlpatterns = [
    path('', include(router.urls))
]

