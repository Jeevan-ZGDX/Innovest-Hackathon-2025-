from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, PartyViewSet, me

router = DefaultRouter()
router.register(r'parties', PartyViewSet, basename='party')

urlpatterns = [
	path('auth/register/', RegisterView.as_view(), name='register'),
	path('auth/me/', me, name='me'),
	path('', include(router.urls)),
]