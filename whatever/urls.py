from django.urls import path
from .views import UserRegisterView, UserLoginView, UserLogoutView, UserProfileListCreateView, UserProfileDetailView, HouseListCreateView, HouseDetailView, SaleListCreateView, SaleDetailView

urlpatterns = [
    path('profiles/', UserProfileListCreateView.as_view(), name='profile-list-create'),
    path('profiles/<int:pk>/', UserProfileDetailView.as_view(), name='profile-detail'),
    path('houses/<int:pk>/', HouseDetailView.as_view(), name='house-detail'),
    path('sales/', SaleListCreateView.as_view(), name='sale-list-create'),
    path('sales/<int:pk>/', SaleDetailView.as_view(), name='sale-detail'),
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
]

