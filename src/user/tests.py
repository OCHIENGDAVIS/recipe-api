from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')



def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserAPITests(TestCase):
    """Tests the user API public"""
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """"Teting cresting a user with a valid payload is succesfull"""
        payload = {
            'email': 'test@davis.com',
           ' password': 'pass1234',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        # self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
       

    def test_user_exists(self):
        """Tests creating a user that exists"""
        payload = {
            'email': 'test@davis.com',
            'password': 'pass1234'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Testing a short password"""
        payload = {
            'email':'test@davis.com',
            'password': 'pwd'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email':'test@davis', 'password': 'pass1234'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test than token is not created coz of invalid credentials"""
        correct_payload = {'email': 'test@davis.com', 'password': 'pass1234'}
        create_user(**correct_payload)
        payload = {
            'email':'test@davis.com', 'password': 'wrongpass'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """"Test than token is not created if the user does not exists"""
        payload = {'email':'test@davis.com', 'password':'pass1234'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_password(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email':'test@davis.com', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)




