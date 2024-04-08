from rest_framework import serializers
from .models import UserProfile, House, Sale


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class HouseSerializer(serializers.ModelSerializer):
    owner = ProfileSerializer(read_only=True)

    class Meta:
        model = House
        fields = '__all__'


class SaleSerializer(serializers.ModelSerializer):
    house = HouseSerializer()
    seller = ProfileSerializer()
    waiting_list = ProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = '__all__'
