from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from whatever.models import UserProfile


class UserRegistrationLoginTests(APITestCase):
    def test_user_registration(self):
        url = reverse('user-register')
        data = {'email': 'mdr@lol.com', 'password': 'testpassword', 'username': 'cryptobro'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertTrue('token' in response.data)
        # self.assertTrue('profile' in response.data)
        user = UserProfile.objects.get(username='cryptobro')
        # self.assertTrue(user.pubkey is not None)
        # self.assertTrue(user.seed.startswith('sEd'))

    def test_user_login(self):
        # First, create a user to test login
        user = UserProfile.objects.create_user(username='testuser', password='testpassword', email='a@a.a')

        # Now, attempt to login
        url = reverse('user-login')
        data = {'email': 'a@a.a', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue('profile' in response.data)
