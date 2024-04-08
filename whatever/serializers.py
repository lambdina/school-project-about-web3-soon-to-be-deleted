from rest_framework import serializers
from .models import UserProfile, House, Sale


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('email', 'username', 'password', 'id')
        extra_kwargs = {'password': {'write_only': True}}


class HouseSerializer(serializers.ModelSerializer):
    owner = ProfileSerializer(read_only=True)

    class Meta:
        model = House
        fields = '__all__'


class SaleSerializer(serializers.ModelSerializer):
    house = HouseSerializer()
    waiting_list = ProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = '__all__'

    def create(self, validated_data):
        validated_data['house']['owner'] = validated_data['seller']
        house_data = validated_data.pop('house')
        validated_data['house'] = HouseSerializer().create(house_data)
        return Sale.objects.create(**validated_data)
