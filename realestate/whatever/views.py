from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile, House, Sale
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import ProfileSerializer, HouseSerializer, SaleSerializer

class UserProfileListCreateView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer

class UserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer

class HouseListCreateView(generics.ListCreateAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated]

class HouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = House.objects.all()
    serializer_class = HouseSerializer

class SaleListCreateView(generics.ListCreateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

class SaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .serializers import ProfileSerializer

class UserLoginView(generics.GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            serializer = ProfileSerializer(user)
            return Response({'token': token.key, 'profile': serializer.data})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserLogoutView(generics.GenericAPIView):
    def post(self, request):
        logout(request)
        return Response({'success': 'Logged out successfully'}, status=status.HTTP_200_OK)

class UserRegisterView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer