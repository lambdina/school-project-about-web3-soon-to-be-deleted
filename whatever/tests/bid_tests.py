# test bids after a logged user made a sell on the marketplace
#
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from whatever.models import UserProfile, Sale, House


class BidTests(APITestCase):

    def setUp(self):
        self.user = UserProfile.objects.create_user(username='testuser', password='testpassword', email='a@a.a')
        self.buyer = UserProfile.objects.create_user(username='testbuyer', password='testpassword', email='b@b.b')
        self.client.force_authenticate(user=self.user)

    def test_bid_on_own_sale(self):
        # Now, create a sale
        sale = Sale.objects.create(
            seller=self.user,
            house=House.objects.create(city='Paris', rooms=3, year_of_construction=2005, owner=self.user),
            is_sold=True
        )
        # Now, attempt to bid on sold sale
        url = reverse('sale-bids')
        data = {'sale': sale.pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('error' in response.data)

    def test_bid_on_sold_sale(self):
        # Now, create a sale
        sale = Sale.objects.create(
            seller=self.user,
            house=House.objects.create(city='Paris', rooms=3, year_of_construction=2005, owner=self.user),
            is_sold=True
        )

        # Now, attempt to bid on sold sale
        url = reverse('sale-bids')
        data = {'sale': sale.pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('error' in response.data)

    def test_bid_on_sale(self):

        # Now, create a sale
        sale = Sale.objects.create(
            seller=self.buyer,
            house=House.objects.create(city='Paris', rooms=3, year_of_construction=2005, owner=self.buyer),
            is_sold=False
        )

        # Now, attempt to bid on sale
        url = reverse('sale-bids')
        data = {'sale': sale.pk}
        response = self.client.post(url, data, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
