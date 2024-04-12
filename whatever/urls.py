from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from .views import UserRegisterView, UserLoginView, UserLogoutView, UserProfileListCreateView, UserProfileDetailView, HouseListCreateView, HouseDetailView, SaleListCreateView, SaleDetailView

schema_view = get_schema_view(
    openapi.Info(title="Real Estate API", default_version='v1'),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('profiles/', UserProfileListCreateView.as_view(), name='profile-list-create'),
    path('profiles/<int:pk>/', UserProfileDetailView.as_view(), name='profile-detail'),
    path('houses/<int:pk>/', HouseDetailView.as_view(), name='house-detail'),
    path('sales/', SaleListCreateView.as_view(), name='sale-list-create'),
    path('sales/<int:pk>/', SaleDetailView.as_view(), name='sale-detail'),
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('swagger/', schema_view.as_view(), name='swagger')
]

