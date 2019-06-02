from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag,Ingredient
from recipe_app.serializers import TagSerializer, IngredientSerializer

TAGS_URL = reverse('recipe_app:tag-list')
INGRIDENT_URL = reverse('recipe_app:ingredient-list')

class PublicTagsAPITest(TestCase):
    """Tests the publicly available tags API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test log in required for retrieving tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsAPITest(TestCase):
    """Test the authorised tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(email='test@davis.com', password='pass1234')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Tests retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Tests that tags returned are fot the authenticated user"""
        user2 = get_user_model().objects.create_user('other@davis.com', 'other')
        Tag.objects.create(user=user2,name='Fruity' )
        tag = Tag.objects.create(user=self.user, name='Comfort Food')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'],tag.name )

    def test_create_tag_succesfull(self):
        """Test creating a new tag"""
        payload = {'name':'test tag'}
        self.client.post(TAGS_URL, payload)
        exists = Tag.objects.filter(user=self.user, name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_test_invalid(self):
        """Test creating a tag with an invalid name"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PublicIngredientAPITest(TestCase):
    """Tests the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()


    def test_login_required(self):
        """Tests the login is required to access the endpoint"""
        res = self.client.get(INGRIDENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsAPITest(TestCase):
    """Test private ingredients API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('test@ochieng.com', 'pass1234')
        self.client.force_authenticate(self.user)

    def test_ingriedient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')
        res = self.client.get(INGRIDENT_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that only ingredients for the authenticated user get returned"""
        user2 = get_user_model().objects.create_user('test@davis.com', 'pass1234')
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Tumeric')
        res = self.client.get(INGRIDENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)


    def test_create_ingredients_successfull(self):
        """Tests creating a new ingredient"""
        paylaod = dict(name='cabbage')
        self.client.post(INGRIDENT_URL, paylaod)
        exists = Ingredient.objects.filter(user=self.user, name=paylaod['name']).exists()
        self.assertTrue(exists)

    def test_ingredients_invalid(self):
        """Tests creating an invalid ingredients fails"""
        payload = {'name':''}
        res = self.client.post(INGRIDENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)






