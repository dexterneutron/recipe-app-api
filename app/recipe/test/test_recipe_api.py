'''

Test for recipe API

'''

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from core.models import Recipe, Tag
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    )
from decimal import Decimal
from django.test import TestCase

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    '''
    Helper function for creating recipe detail url

    '''
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_recipe(user, **kwargs):
    '''
    Helper function for creating test recipe

    '''
    defaults = {
        'title': 'Test recipe',
        'time_minutes': 10,
        'price': Decimal(5.00),
        'link': 'http://test.com/recipe.pdf',
        'description': 'Test description',
    }

    defaults.update(kwargs)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**kwargs):
    '''
    Helper function for creating test user

    '''
    return get_user_model().objects.create_user(**kwargs)

class PublicRecipeApiTests(TestCase):
    '''
    Test unauthenticated recipe API access

    '''

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        '''
        Test that authentication is required

        '''
        res = self.client.get(reverse('recipe:recipe-list'))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    '''
    Test authenticated recipe API access

    '''

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='test@example.com',password='testpass')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        '''
        Test retrieving a list of recipes

        '''
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        '''
        Test retrieving recipes for user

        '''
        user2 =create_user(email='user2@example.com',password='testpass')
        create_recipe(user2)
        create_recipe(self.user)

        res = self.client.get(RECIPES_URL)
        recipes =  Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        '''
        Test retrieving a recipe detail

        '''
        recipe = create_recipe(user=self.user)

        res = self.client.get(detail_url(recipe.id))

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        '''
        Test creating recipe

        '''
        payload = {
            'title': 'Test recipe',
            'time_minutes': 10,
            'price': 5.00,
            'description': 'Test description',
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key, value in payload.items():
            self.assertEqual(value, getattr(recipe, key))

        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        '''
        Test updating a recipe with patch

        '''
        original_link = 'http://test.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Test title',
            link=original_link,
            )

        payload = {'title': 'New title',}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        '''Test full update of recipe'''

        recipe = create_recipe(
            user=self.user,
            title='Test title',
            link='http://test.com/recipe.pdf',
            description = 'Test description',
        )

        payload = {
            'title': 'Updated title',
            'link': 'http://test.com/updated-recipe.pdf',
            'description': 'Updated description',
            'time_minutes': 20,
            'price': Decimal(10.00),
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)

        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())


    def test_create_recipe_with_new_tags(self):
        '''Test creating a recipe with new tags'''

        payload ={
            'title': 'Test recipe',
            'time_minutes': 10,
            'price': Decimal(5.00),
            'tags': [{'name':'tag1'}, {'name':'tag2'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(len(recipes), 1)

        recipe = recipes.first()
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn('tag1', [tag.name for tag in tags])
        self.assertIn('tag2', [tag.name for tag in tags])

    def test_create_recipe_with_existing_tags(self):
        '''Test creating a recipe with existing tags'''

        tag = Tag.objects.create(user=self.user, name='tag1')
        payload ={
            'title': 'Test recipe',
            'time_minutes': 10,
            'price': Decimal(5.00),
            'tags': [{"name":"tag1"}, {"name":"tag2"}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(len(recipes), 1)

        recipe = recipes.first()
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn('tag1', [tag.name for tag in tags])

    def test_create_tag_on_update(self):
        ''' Test creating tag when updating a recipe '''
        recipe = create_recipe(user=self.user)

        payload = {'tags': [{'name':'Test'}]}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Test')
        self.assertIn(new_tag, recipe.tags.all())


    def test_update_recipe_assign_tag(self):
        '''Test assigning existing tag when updating a recipe'''
        tag_1 = Tag.objects.create(user=self.user, name='tag1')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_1)

        tag_2 = Tag.objects.create(user=self.user, name='tag2')
        payload = {'tags': [{'name':'tag2'}]}
        url = detail_url(recipe.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_2, recipe.tags.all())
        self.assertNotIn(tag_1, recipe.tags.all())

    def test_clear_recipes_tags(self):
        '''Test clear tags from a recipe '''
        tag = Tag.objects.create(user=self.user, name='tag1')

        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)