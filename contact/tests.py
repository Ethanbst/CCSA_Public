from django.test import TestCase
from django.urls import reverse
from .models import *
from django.test import override_settings

@override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
class ContactFormTestCase(TestCase):
    def setUp(self):
        self.mail_data = {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '1234567890',
                'message': 'Hello, this is a test message.',
                'rgpd': True,
            }
        self.contact_list = [
            {
                'mail' : 'admin@example.com',
                'is_active' : True
            }
        ]

    #---------------------------------
    # Test d'envoi d'un mail
    #---------------------------------
    
    def test_post_mail(self):
        """
        Test de l'envoi d'un mail avec données valides et contact CCSA
        """
        # Créez un contact CCSA
        ContactEmail.objects.create(
            email='admin@example.com',
            is_active=True
        )
        response = self.client.post(reverse('home'), data=self.mail_data)
        self.assertTemplateUsed(response, 'email_text_client.txt')
        self.assertTemplateUsed(response, 'email_html_client.html')
        self.assertTemplateUsed(response, 'email_text.txt')
        self.assertTemplateUsed(response, 'email_html.html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_email_post_without_contact(self):
        """
        Test de l'envoi d'un mail sans contact CCSA
        """
        response = self.client.post(reverse('home'), data=self.mail_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_email_post_invalid_first_name(self):
        """
        Test de l'envoi d'un mail sans first_name
        """
        # Créez un contact CCSA
        ContactEmail.objects.create(
            email='admin@example.com',
            is_active=True
        )
        self.mail_data['first_name'] = ''
        response = self.client.post(reverse('home'), data=self.mail_data)
        self.assertTemplateNotUsed(response, 'email_text_client.txt')
        self.assertTemplateNotUsed(response, 'email_html_client.html')
        self.assertTemplateNotUsed(response, 'email_text.txt')
        self.assertTemplateNotUsed(response, 'email_html.html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_email_post_invalid_last_name(self):
        """
        Test de l'envoi d'un mail sans last_name
        """
        self.mail_data['last_name'] = ''
        response = self.client.post(reverse('home'), data=self.mail_data)
        self.assertTemplateNotUsed(response, 'email_text_client.txt')
        self.assertTemplateNotUsed(response, 'email_html_client.html')
        self.assertTemplateNotUsed(response, 'email_text.txt')
        self.assertTemplateNotUsed(response, 'email_html.html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_email_post_invalid_email(self):
        """
        Test de l'envoi d'un mail sans email
        """
        # Créez un contact CCSA
        ContactEmail.objects.create(
            email='admin@example.com',
            is_active=True
        )
        self.mail_data['email'] = ''
        response = self.client.post(reverse('home'), data=self.mail_data)
        self.assertTemplateNotUsed(response, 'email_text_client.txt')
        self.assertTemplateNotUsed(response, 'email_html_client.html')
        self.assertTemplateNotUsed(response, 'email_text.txt')
        self.assertTemplateNotUsed(response, 'email_html.html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_email_post_invalid_phone(self):
        """
        Test de l'envoi d'un mail avec un numéro de téléphone invalide
        """
        # Créez un contact CCSA
        ContactEmail.objects.create(
            email='admin@example.com',
            is_active=True
        )
        self.mail_data['phone'] = ''
        response = self.client.post(reverse('home'), data=self.mail_data)
        # Le numéro n'est pas requis alors la requête est acceptée
        self.assertTemplateUsed(response, 'email_text_client.txt')
        self.assertTemplateUsed(response, 'email_html_client.html')
        self.assertTemplateUsed(response, 'email_text.txt')
        self.assertTemplateUsed(response, 'email_html.html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

        # Test avec numéro contenant des lettres
        self.mail_data['phone'] = 'IOIOI'
        response = self.client.post(reverse('home'), data=self.mail_data)
        self.assertTemplateNotUsed(response, 'email_text_client.txt')
        self.assertTemplateNotUsed(response, 'email_html_client.html')
        self.assertTemplateNotUsed(response, 'email_text.txt')
        self.assertTemplateNotUsed(response, 'email_html.html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

        # Test avec numéro trop court
        self.mail_data['phone'] = '12345678'
        response = self.client.post(reverse('home'), data=self.mail_data)
        self.assertTemplateNotUsed(response, 'email_text_client.txt')
        self.assertTemplateNotUsed(response, 'email_html_client.html')
        self.assertTemplateNotUsed(response, 'email_text.txt')
        self.assertTemplateNotUsed(response, 'email_html.html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

        # Test avec numéro contenant des lettres et trop court
        self.mail_data['phone'] = '123456789A'
        response = self.client.post(reverse('home'), data=self.mail_data)
        self.assertTemplateNotUsed(response, 'email_text_client.txt')
        self.assertTemplateNotUsed(response, 'email_html_client.html')
        self.assertTemplateNotUsed(response, 'email_text.txt')
        self.assertTemplateNotUsed(response, 'email_html.html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_email_post_invalid_message(self):
        """
        Test de l'envoi d'un mail avec un message invalide
        """
        # Créez un contact CCSA
        ContactEmail.objects.create(
            email='admin@example.com',
            is_active=True
        )
        self.mail_data['message'] = 'Hi'
        response = self.client.post(reverse('home'), data=self.mail_data)
        self.assertTemplateNotUsed(response, 'email_text_client.txt')
        self.assertTemplateNotUsed(response, 'email_html_client.html')
        self.assertTemplateNotUsed(response, 'email_text.txt')
        self.assertTemplateNotUsed(response, 'email_html.html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_email_post_invalid_rgpd(self):
        """
        Test de l'envoi d'un mail sans acceptation des conditions RGPD
        """
        # Créez un contact CCSA
        ContactEmail.objects.create(
            email='admin@example.com',
            is_active=True
        )
        self.mail_data['rgpd'] = False
        response = self.client.post(reverse('home'), data=self.mail_data)
        self.assertTemplateNotUsed(response, 'email_text_client.txt')
        self.assertTemplateNotUsed(response, 'email_html_client.html')
        self.assertTemplateNotUsed(response, 'email_text.txt')
        self.assertTemplateNotUsed(response, 'email_html.html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

