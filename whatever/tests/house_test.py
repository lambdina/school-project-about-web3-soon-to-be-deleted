from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from whatever.models import House, UserProfile


class HouseCreationTests(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(username='testuser', password='testpassword', email='a@a.a')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_house(self):
        url = reverse('house-list-create')
        data = {'city': 'New York', 'rooms': 3, 'year_of_construction': 2005, }
        response = self.client.post(url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(House.objects.count(), 1)
        house = House.objects.get()
        self.assertEqual(house.city, 'New York')
        self.assertEqual(house.rooms, 3)
        self.assertEqual(house.year_of_construction, 2005)

    def test_create_house_without_authentication(self):
        url = reverse('house-list-create')
        data = {'city': 'New York', 'rooms': 3, 'year_of_construction': 2005, 'images': 'house_image.jpg'}
        self.client.credentials()  # Remove authentication credentials
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(House.objects.count(), 0)

    def test_create_house_invalid_data(self):
        url = reverse('house-list-create')
        # Invalid data: city field is missing
        data = {'rooms': 3, 'year_of_construction': 2005, 'images': 'house_image.jpg'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(House.objects.count(), 0)
