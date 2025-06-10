from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.test import Client
from services.models import Service

User = get_user_model()
MEDIA_ROOT = 'test_media_services'

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ServiceViewsTestCase(TestCase):
    """
    Tests pour les vues de l'application services.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(
            email="admin@exemple.com",
            password="adminpassword"
        )

    def setUp(self):
        """
        Configuration de l'environnement de test.
        """
        self.client = Client()
        self.client.login(email=self.superuser.email, password="adminpassword")

    # Test des vues d'affichage des services sur l'accueil
    def test_service_home_list_view_without_data(self):
        """
        Test de la vue de liste des services de la page d'accueil sans données.
        """
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/index.html')
        self.assertContains(response, "Aucun service n'est disponible pour le moment.")

    def test_service_home_list_view_with_data(self):
        """
        Test de la vue de liste des services de la page d'accueil avec des données.
        """
        Service.objects.create(
            title="Test Service",
            content="Description du service de test.",
            icon="<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 640 512\"><path fill=\"#fff\" d=\"M74.6 373.2c41.7 36.1 108 82.5 166.1 73.7c6.1-.9 12.1-2.5 18-4.5c-9.2-12.3-17.3-24.4-24.2-35.4c-21.9-35-28.8-75.2-25.9-113.6c-20.6 4.1-39.2 13-54.7 25.4c-6.5 5.2-16.3 1.3-14.8-7c6.4-33.5 33-60.9 68.2-66.3c2.6-.4 5.3-.7 7.9-.8l19.4-131.3c2-13.8 8-32.7 25-45.9C278.2 53.2 310.5 37 363.2 32.2c-.8-.7-1.6-1.4-2.4-2.1C340.6 14.5 288.4-11.5 175.7 5.6S20.5 63 5.7 83.9C0 91.9-.8 102 .6 111.8L24.8 276.1c5.5 37.3 21.5 72.6 49.8 97.2zm87.7-219.6c4.4-3.1 10.8-2 11.8 3.3c.1 .5 .2 1.1 .3 1.6c3.2 21.8-11.6 42-33.1 45.3s-41.5-11.8-44.7-33.5c-.1-.5-.1-1.1-.2-1.6c-.6-5.4 5.2-8.4 10.3-6.7c9 3 18.8 3.9 28.7 2.4s19.1-5.3 26.8-10.8zM261.6 390c29.4 46.9 79.5 110.9 137.6 119.7s124.5-37.5 166.1-73.7c28.3-24.5 44.3-59.8 49.8-97.2l24.2-164.3c1.4-9.8 .6-19.9-5.1-27.9c-14.8-20.9-57.3-61.2-170-78.3S299.4 77.2 279.2 92.8c-7.8 6-11.5 15.4-12.9 25.2L242.1 282.3c-5.5 37.3-.4 75.8 19.6 107.7zM404.5 235.3c-7.7-5.5-16.8-9.3-26.8-10.8s-19.8-.6-28.7 2.4c-5.1 1.7-10.9-1.3-10.3-6.7c.1-.5 .1-1.1 .2-1.6c3.2-21.8 23.2-36.8 44.7-33.5s36.3 23.5 33.1 45.3c-.1 .5-.2 1.1-.3 1.6c-1 5.3-7.4 6.4-11.8 3.3zm136.2 15.5c-1 5.3-7.4 6.4-11.8 3.3c-7.7-5.5-16.8-9.3-26.8-10.8s-19.8-.6-28.7 2.4c-5.1 1.7-10.9-1.3-10.3-6.7c.1-.5 .1-1.1 .2-1.6c3.2-21.8 23.2-36.8 44.7-33.5s36.3 23.5 33.1 45.3c-.1 .5-.2 1.1-.3 1.6zM530 350.2c-19.6 44.7-66.8 72.5-116.8 64.9s-87.1-48.2-93-96.7c-1-8.3 8.9-12.1 15.2-6.7c23.9 20.8 53.6 35.3 87 40.3s66.1 .1 94.9-12.8c7.6-3.4 16 3.2 12.6 10.9z\"/></svg>"
        )
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/index.html')
        self.assertContains(response, "Découvrez les services proposés par la Communauté de Communes Sud-Avesnois pour améliorer votre quotidien.")

    # Test des vues d'affichage des services sur la page administrateur
    def test_service_admin_list_view_without_data(self):
        """
        Test de la vue de liste des services de la page administrateur sans données.
        """
        response = self.client.get(reverse('services:admin_services_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/service-list.html')
        self.assertContains(response, "Aucun service n'a été créé pour le moment.")

    def test_service_admin_list_view_with_data(self):
        """
        Test de la vue de liste des services de la page administrateur avec des données.
        """
        Service.objects.create(
            title="Test Service",
            content="Description du service de test.",
            icon="<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 640 512\"><path fill=\"#fff\" d=\"M74.6 373.2c41.7 36.1 108 82.5 166.1 73.7c6.1-.9 12.1-2.5 18-4.5c-9.2-12.3-17.3-24.4-24.2-35.4c-21.9-35-28.8-75.2-25.9-113.6c-20.6 4.1-39.2 13-54.7 25.4c-6.5 5.2-16.3 1.3-14.8-7c6.4-33.5 33-60.9 68.2-66.3c2.6-.4 5.3-.7 7.9-.8l19.4-131.3c2-13.8 8-32.7 25-45.9C278.2 53.2 310.5 37 363.2 32.2c-.8-.7-1.6-1.4-2.4-2.1C340.6 14.5 288.4-11.5 175.7 5.6S20.5 63 5.7 83.9C0 91.9-.8 102 .6 111L24 .8z\"/></svg>"
        )
        response = self.client.get(reverse('services:admin_services_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(Service.objects.get().title, "Test Service")
        self.assertTemplateUsed(response, 'services/service-list.html')
        self.assertContains(response, "Test Service")

    # Test de la vue d'ajout d'un service
    def test_service_add_view_valid_data(self):
        """
        Test de la vue d'ajout d'un service avec des données valides.
        """
        response = self.client.post(reverse('services:add_service'), {
            'title': 'Test Service',
            'content': 'Description du service de test.',
            'icon': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><path fill="#fff" d="M74.6 373.2c41.7 36.1 108 82.5 166.1 73.7c6.1-.9 12.1-2.5 18-4.5c-9.2-12.3-17.3-24.4-24.2-35.4c-21.9-35-28.8-75.2-25.9-113.6c-20.6 4.1-39.2 13-54.7 25.4c-6.5 5.2-16.3 1.3-14.8-7c6.4-33.5 33-60.9 68.2-66.3c2.6-.4 5.3-.7 7.9-.8l19.4-131.3c2-13.8 8-32.7 25-45.9C278.2 53.2 310.5 37 363.2 32.2c-.8-.7-1.6-1.4-2.4-2C340 .6z"/></svg>'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('services:admin_services_list'))
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(Service.objects.get().title, 'Test Service')

    # Test de la vue d'ajout d'un service avec des données invalides
    def test_service_add_view_invalid_data(self):
        """
        Test de la vue d'ajout d'un service avec des données invalides.
        """
        response = self.client.post(reverse('services:add_service'), {
            'title': '',
            'content': '',
            'icon': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/ajout-service.html')
        self.assertIn('title', response.context['service_form'].errors)
        self.assertIn('content', response.context['service_form'].errors)
        self.assertIn('icon', response.context['service_form'].errors)
        self.assertEqual(Service.objects.count(), 0)

    # Test de la vue de modification d'un service
    def test_service_update_view_valid_data(self):
        """
        Test de la vue de modification d'un service avec des données valides.
        """
        service = Service.objects.create(
            title="Test Service",
            content="Description du service de test.",
            icon="<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 640 512\"><path fill=\"#fff\" d=\"M74.6 373.2c41.7 36.1 108 82.5 166.1 73.7c6.1-.9 12.1-2.5 18-4.5c-9.2-12.3-17.3-24.4-24.2-35.4c-21.9-35-28.8-75.2-25.9-113.6c-20.6 4.1-39.2 13-54.7 25.4c-6.5 5.2-16.3 1.3-14.8-7c6.4-33.5 33-60.9 68.2-66.3c2.6-.4 5.3-.7 7.9-.8l19.4-131.3c2-13.8 8-32.7 25-45.9C278 .2z\"/></svg>"
        )
        response = self.client.post(reverse('services:update_service', args=[service.id]), {
            'title': 'Test Service Modifié',
            'content': 'Description du service de test modifié.',
            'icon': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><path fill="#fff" d="M74 .6z"/></svg>'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('services:admin_services_list'))
        service.refresh_from_db()
        self.assertEqual(service.title, 'Test Service Modifié')

    # Test de la vue de modification d'un service avec des données invalides
    def test_service_update_view_invalid_data(self):
        """
        Test de la vue de modification d'un service avec des données invalides.
        """
        service = Service.objects.create(
            title="Test Service",
            content="Description du service de test.",
            icon="<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 640 512\"><path fill=\"#fff\" d=\"M74 .6z\"/></svg>"
        )
        response = self.client.post(reverse('services:update_service', args=[service.id]), {
            'title': '',
            'content': '',
            'icon': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services/modifier-service.html')
        self.assertIn('title', response.context['service_form'].errors)
        self.assertIn('content', response.context['service_form'].errors)
        self.assertIn('icon', response.context['service_form'].errors)
        self.assertEqual(Service.objects.count(), 1)

    # Test de la vue de suppression d'un service
    def test_service_delete_view(self):
        """
        Test de la vue de suppression d'un service.
        """
        service = Service.objects.create(
            title="Test Service",
            content="Description du service de test.",
            icon="<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 640 512\"><path fill=\"#fff\" d=\"M74 .6z\"/></svg>"
        )
        response = self.client.post(reverse('services:delete_service', args=[service.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('services:admin_services_list'))
        self.assertEqual(Service.objects.count(), 0)