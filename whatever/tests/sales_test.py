from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from whatever.models import UserProfile, Sale


class SaleCreationTests(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(username='testuser', password='testpassword', email='a@a.a')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_sale(self):
        url = reverse('sale-list-create')
        data = {
            'is_sold': False,
            'auction_end_time': (datetime.now() + timedelta(days=21)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'house': {
                'city': 'New York',
                'rooms': 3,
                'year_of_construction': 2005
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sale.objects.count(), 1)
        sale = Sale.objects.get(pk=response.data['id'])
        self.assertEqual(sale.is_sold, False)
        self.assertEqual(sale.house.city, 'New York')
        self.assertEqual(sale.house.rooms, 3)
        self.assertEqual(sale.house.year_of_construction, 2005)
        self.assertEqual(sale.seller.id, self.user.id)
        self.assertEqual(sale.waiting_list.count(), 0)

    def test_create_sale_without_authentication(self):
        url = reverse('sale-list-create')
        data = {
            'is_sold': False,
            'auction_end_time': (datetime.now() + timedelta(days=21)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'house': {
                'city': 'New York',
                'rooms': 3,
                'year_of_construction': 2005
            }
        }
        self.client.force_authenticate(user=None)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Sale.objects.count(), 0)
