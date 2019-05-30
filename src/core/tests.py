from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTestCase(TestCase):
    def test_create_user_with_email_succesfull(self):
        email = 'test@davis.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        """Test that the email for a new user is normalised"""
        email = 'test@DAVIS..COM'
        user = get_user_model().objects.create_user(email, 'pass123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating a new user with no email raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'pass123')

    def test_create_superuser(self):
        """Test creating a new super user"""
        user = get_user_model().objects.create_superuser('test@admin.com', 'pass1234')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


