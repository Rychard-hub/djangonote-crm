from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api_views import (
    LeadViewSet, CommentViewSet, TaskViewSet, 
    ActivityViewSet, ProfileViewSet, RegistrationViewSet
)

# Sukuriam router'į
router = DefaultRouter()
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'profile', ProfileViewSet, basename='profile')

# API URL maršrutai
urlpatterns = [
    # JWT auth endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registration endpoints
    path('auth/register/', RegistrationViewSet.as_view({'post': 'register'}), name='register'),
    path('auth/verify-email/', RegistrationViewSet.as_view({'post': 'verify_email'}), name='verify-email'),
    
    # Dashboard summary endpoint
    path('dashboard/summary/', LeadViewSet.as_view({'get': 'dashboard_stats'}), name='dashboard-summary'),
    
    # API endpoints su router'iu
    path('', include(router.urls)),
]
