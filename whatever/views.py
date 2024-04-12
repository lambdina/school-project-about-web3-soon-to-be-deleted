from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import UserProfile, House, Sale
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from .serializers import ProfileSerializer, HouseSerializer, SaleSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout

from .services.xrpl import XRPLService, create_wallet


class UserProfileListCreateView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class UserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class HouseListCreateView(generics.ListCreateAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        request.data['owner'] = ProfileSerializer(request.user).data
        return super().create(request, *args, **kwargs)


class HouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = House.objects.all()
    serializer_class = HouseSerializer


class SaleListCreateView(generics.ListCreateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        request.data['seller'] = request.user.id
        request.data['waiting_list'] = []
        return super().create(request, *args, **kwargs)


class SaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer


class UserLoginView(generics.GenericAPIView):
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Login user",
        responses={200: openapi.Response(
            description="User logged in successfully",
            examples={
                    "token": "TokenKey",
                    "profile": {
                        "id": 1,
                        "email": "blurp@blurp.com",
                        "username": "blurp",
                        "pubkey": "r123123123",
                        "privkey": "s123123123",
                        "seed": "sEd123123123"
                    }
            }
        ), 401: openapi.Response(
            description="Invalid credentials",
            examples={
                    "error": "Invalid credentials"
            }
        )}
    )
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
    authentication_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout user",
        responses={200: openapi.Response(
            description="User logged out successfully",
            examples={
                    "success": "Logged out successfully"
            }
        )}
    )
    def post(self, request):
        logout(request)
        return Response({'success': 'Logged out successfully'}, status=status.HTTP_200_OK)


class UserRegisterView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = UserProfile.objects.get(pk=response.data['id'])
        user.set_password(request.data['password'])
        # TODO, hash private key and seed lol
        pubkey, privkey, seed = create_wallet()
        user.pubkey = pubkey
        user.privkey = privkey
        user.seed = seed
        user.save()
        return response
