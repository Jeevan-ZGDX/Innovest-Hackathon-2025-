from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


class PartyFlowTests(APITestCase):
	def setUp(self):
		self.username = 'u1'
		self.password = 'p1'
		User.objects.create_user(username=self.username, password=self.password)

	def auth(self):
		url = reverse('token_obtain_pair')
		res = self.client.post(url, {'username': self.username, 'password': self.password}, format='json')
		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

	def test_create_party_and_join(self):
		self.auth()
		res = self.client.post('/api/parties/', {'name': 'Room'}, format='json')
		self.assertEqual(res.status_code, status.HTTP_201_CREATED)
		party_id = res.data['id']
		res2 = self.client.post(f'/api/parties/{party_id}/join/', {'label': 'Main'}, format='json')
		self.assertEqual(res2.status_code, status.HTTP_200_OK)
