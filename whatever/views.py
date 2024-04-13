import os

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import UserProfile, House, Sale
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from .serializers import ProfileSerializer, HouseSerializer, SaleSerializer, BidSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout

from .services.xrpl import XRPLService


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

        # test mint
        if int(os.getenv('TEST', 0)):
            return super().create(request, *args, **kwargs)
        tx_result = XRPLService().mint_house(request.user.seed, request.data['price'], uri="https://www.google.com")
        if tx_result:
            request.data['creation_tx_hash'] = tx_result["result"]["hash"]
            return super().create(request, *args, **kwargs)
        return Response({'error': 'Failed to mint house'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer


class SaleBidView(generics.ListCreateAPIView):
    authentication_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = BidSerializer

    @swagger_auto_schema(
        operation_description="Bid on a sale",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'sale': openapi.Schema(type=openapi.TYPE_INTEGER, description='Sale ID')
            }
        ),
        responses={200: openapi.Response(
            description="Added to waiting list",
            examples={
                "success": "Added to waiting list"
            }
        ), 400: openapi.Response(
            description="Error",
            examples={
                "error": "Sale is already sold"
            }
        )}
    )
    def create(self, request, *args, **kwargs):
        sale = Sale.objects.get(pk=request.data['sale'])
        if sale.is_sold:
            return Response({'error': 'Sale is already sold'}, status=status.HTTP_400_BAD_REQUEST)
        if sale.seller == request.user:
            return Response({'error': 'You cannot bid on your own sale'}, status=status.HTTP_400_BAD_REQUEST)
        sale.waiting_list.add(request.user)
        sale.save()
        return Response({'success': 'Added to waiting list'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Buy a sale",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'sale': openapi.Schema(type=openapi.TYPE_INTEGER, description='Sale ID')
            }
        ),
        responses={200: openapi.Response(
            description="Sale is sold",
            examples={
                "success": "Sale is sold"
            }
        ), 400: openapi.Response(
            description="Error",
            examples={
                "error": "Sale is already sold"
            }
        )}
    )
    def update(self, request, *args, **kwargs):
        sale = Sale.objects.get(pk=request.data['sale'])
        if sale.is_sold:
            return Response({'error': 'Sale is already sold'}, status=status.HTTP_400_BAD_REQUEST)
        if sale.seller == request.user:
            return Response({'error': 'You cannot bid on your own sale'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user in sale.waiting_list.all():
            sale.waiting_list.remove(request.user)
            sale.is_sold = True
            sale.save()
            return Response({'success': 'Sale is sold'}, status=status.HTTP_200_OK)
        return Response({'error': 'You are not in the waiting list'}, status=status.HTTP_400_BAD_REQUEST)


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

        if int(os.getenv('TEST', 0)):
            user.save()
            return response

        pubkey, privkey, seed = XRPLService().get_or_create_wallet()
        user.pubkey = pubkey
        user.privkey = privkey
        user.seed = seed
        user.save()
        return response
