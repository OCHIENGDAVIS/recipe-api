from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

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

class AdminSiteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(email="admin@davis.com", password="pass123")
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(email="test@davis.com", password="pass123", name="Test User")

    def test_users_listed(self):
        """Test than users are listed on the user page  """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Tests that the user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)



