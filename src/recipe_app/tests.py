import tempfile
import os
from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag,Ingredient, Recipe
from recipe_app.serializers import TagSerializer, IngredientSerializer, RecipeSerializer, RecipeDetailSerializer

TAGS_URL = reverse('recipe_app:tag-list')
INGRIDENT_URL = reverse('recipe_app:ingredient-list')
RECIPE_URL = reverse('recipe_app:recipe-list')

def image_upload_url(recipe_id):
    """Return url for recipe image upload"""
    return reverse('recipe_app:recipe-upload-image', args=[recipe_id])



def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse('recipe_app:recipe-detail', args=[recipe_id])



def sample_tag(user, name='Main Course'):
    """Create and return  a sample tag"""
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='Cinnamon'):
    """Create and return  a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)



def sample_recipe(user, **params):
    """Create and return  a simple recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price':5.00
    }
    defaults.update(params)
    return  Recipe.objects.create(user=user, **defaults)


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


class PublicRecipeAPITest(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test than authentication ie required"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeAPITest(TestCase):
    """Test unauthorised recipe API access"""
    def setUp(self):
        self.user = get_user_model().objects.create_user('test@nairobiapp.com', 'testpass')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Tets getting a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test getting recipes for user"""
        user2 = get_user_model().objects.create_user(
            'other@nairobiapp.com',
            'pass1234'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating a recipe"""
        payload = {
            'title':'chcoclate cheesecake',
            'time_minutes': 30,
            'price':5.00,

        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title':'Avocado lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes':60,
            'price':20.00
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Prawns')
        ingredient2 = sample_ingredient(user=self.user, name='Ginger')
        payload = {
            'title': 'Thai prawn red curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes':20,
            'price': 7.00
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test Updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')
        payload = {
            'title':'Chicken tikka',
            'tags':[new_tag.id]
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with  put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Spagheti carbonara',
            'time_minutes': 25,
            'price': 5.00,
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTest(TestCase):
    """Image upload tests"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user@nairobidev.com', 'testpass')
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Tests uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10,10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image':ntf}, format='multipart')
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Tests uploading a bad image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image':'notimage'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """Test returning recipes with specific tags"""
        recipe1 = sample_recipe(user=self.user, title='Thai vegetable curry')
        recipe2 = sample_recipe(user=self.user, title='Aubergine with tahini')
        tag1 = sample_tag(user=self.user, name='Vegan Curry')
        tag2 = sample_tag(user=self.user, name='Vegetarian')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = sample_recipe(user=self.user, title='Fish and Chips')
        res = self.client.get(RECIPE_URL, {'tags':f'{tag1.id}, {tag2.id}'})
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3, res.data)

    def test_filter_recipes_by_ingredients(self):
        """Tests returning a recipe with specific ingredients"""
        recipe1 = sample_recipe(user=self.user, title='Posh beans on Toast')
        recipe2 = sample_recipe(user=self.user, title='Chicken cacciatore')
        ingredient1 = sample_ingredient(user=self.user, name='Feta Cheeese')
        ingredient2 = sample_ingredient(user=self.user, name='Chicken')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = sample_recipe(user=self.user, title='Steak and Mushrooms')

        res = self.client.get(
            RECIPE_URL,
            {'ingredients': f'{ingredient1.id}, {ingredient2.id}'}
        )
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3, res.data)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test fiiltering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Coriander eggs on Toast',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe.tags.add(tag1)
        res = self.client.get(TAGS_URL, {'assigned_only':1})
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned o recipes"""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Apples')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            title='Apple crumble',
            price=10.00,
            time_minutes=5,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)
        res = self.client.get(INGRIDENT_URL, {'assigned_only': 1 })
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
















