from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import EmailActivation

User = get_user_model()

class RegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/register/' # Sesuaikan dengan url Anda

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_user_registration_sends_email(self):
        data = {
            "first_name": "Test",
            "last_name": "User",
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 're123da123'
        }
        
        # 1. Jalankan request pendaftaran
        response = self.client.post(self.register_url, data, format='json')
        print(response.json())
        
        # 2. Cek apakah status code 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 3. Cek apakah user dibuat di DB dengan is_active=False
        user = User.objects.get(username='testuser')
        self.assertFalse(user.is_active)
        
        # 4. Cek apakah EmailActivation terbuat
        self.assertTrue(EmailActivation.objects.filter(user=user).exists())
        
        # 5. Cek apakah email terkirim ke outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Aktifkan Akun Anda')
        self.assertIn('http://localhost:8000/api/activate/', mail.outbox[0].body)