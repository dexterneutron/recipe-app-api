""" Test for models."""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase

from core import models

def create_user(email='test@example.com',password='testpass',):
    """ Create a user. """

    return get_user_model().objects.create_user(email,password,)

class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """ Test creating a new user with an email is successful """
        email = "test@example.com"
        password = "Testpass123"
        user = get_user_model().objects.create_user(
            email=email, password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ Test the email for a new user is normalized """
        sample_emails = {
            "test1@EXAMPLE.com": "test1@example.com",
            "Test2@ExAmPlE.com": "Test2@example.com",
            "TEST3@EXAMPLE.com": "TEST3@example.com",
            "test4@ExAmPlE.com": "test4@example.com",
        }

        for email, expected in sample_emails.items():
            user = get_user_model().objects.create_user(email, "test123")

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """ Test creating a new user without an email raises error """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test123")

    def test_create_new_superuser(self):
        """ Test creating a new superuser """
        user = get_user_model().objects.create_superuser(
            "test@example.com", "test123",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """ Test creating a new recipe """
        user = get_user_model().objects.create_user(
            "test@example.com",
            "test123",
        )

        recipe = models.Recipe.objects.create(
            title="Test recipe",
            time_minutes=5,
            user=user,
            price=Decimal('5.00'),
            description="A test recipe",
        )

        self.assertEqual(str(recipe), "Test recipe")

    def test_create_tag(self):
        """ Test creating a new tag """
        user = create_user()
        tag = models.Tag.objects.create(
            name="Test tag",
            user=user,
        )

        self.assertEqual(str(tag), tag.name)
