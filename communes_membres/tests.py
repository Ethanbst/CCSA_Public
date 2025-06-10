from django.test import TestCase
from django.urls import reverse
from communes_membres.models import ActeLocal
from conseil_communautaire.models import ConseilVille
from django.contrib.auth import get_user_model
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
import os
import shutil
User = get_user_model()  # Récupérer le modèle d'utilisateur personnalisé


# Définir un répertoire temporaire pour les médias
MEDIA_ROOT = 'test_commune_media'


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class JournalAddJournalViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un superutilisateur personnalisé
        cls.superuser = User.objects.create_superuser(
            email='admin@example.com',  # Utiliser l'email comme nom d'utilisateur
            password='password123'
        )

    def setUp(self):
        self.client = Client()
        # Se connecter avec l'email
        self.client.login(email='admin@example.com', password='password123')

    def tearDown(self):
        # Nettoyer les fichiers uploadés après chaque test
        ActeLocal.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def create_commune(self):
        return ConseilVille.objects.create(
            city_name="Test Commune",
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="123 Rue de la République",
            postal_code="75001",
            phone_number="0123456789",
            website="http://www.testcommune.fr",
            image=SimpleUploadedFile(
                name='test_image.jpg',
                content=b'fake_image_content',
                content_type='image/jpeg'
            ),
            slogan="Slogan de la commune",
            nb_habitants=1000,
        )

    def create_acte_local(self, commune):
        return ActeLocal.objects.create(
            title="Test Acte",
            date="2023-10-01",
            description="Description de l\'acte",
            commune=commune,
            file=SimpleUploadedFile(
                name='test_file.pdf',
                content=b'fake_file_content',
                content_type='application/pdf'
            )
        )

    # Test de l'affichage publique + administration
    def test_public_view(self):
        """
        Test de l'affichage publique de la commune et de l'acte local
        """
        commune = self.create_commune()
        acte_local = self.create_acte_local(commune)

        response = self.client.get(
            reverse('communes-membres:commune', args=[commune.slug]))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'communes_membres/commune.html')
        # Vérifier que le contexte contient la commune et l'acte
        self.assertEqual(response.context['commune'], commune)
        self.assertEqual(response.context['acte'], acte_local)

        # Vérifier que l'acte local s'affiche bien dans la partie administration
        response = self.client.get(reverse('communes-membres:admin_acte_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'communes_membres/admin_acte_list.html')
        # Vérifier que l'acte local est présent dans la liste
        self.assertContains(response, "Test Acte")

    # Test de l'ajout d'un acte local
    def test_add_acte_local_valid_data(self):
        """
        Test de l'ajout d'un acte local
        """
        commune = self.create_commune()
        response = self.client.post(reverse('communes-membres:admin_acte_add'), {
            'title': 'Test Acte',
            'date': '2023-10-01',
            'description': 'Description de l\'acte',
            'commune': commune.id,
            'file': SimpleUploadedFile(
                name='test_file.pdf',
                content=b'fake_file_content',
                content_type='application/pdf'
            )
        })
        # Vérifier que la réponse est une redirection
        self.assertEqual(response.status_code, 302)
        # Vérifier que l'utilisateur est redirigé vers la liste des actes locaux
        self.assertRedirects(response, reverse('communes-membres:admin_acte_list'))
        # Vérifier que l'acte local a été créé
        acte_local = ActeLocal.objects.get(title='Test Acte')
        self.assertEqual(acte_local.title, 'Test Acte')

    # Test de l'ajout d'un acte local avec des données invalides
    def test_add_acte_local_invalid_data(self):
        """
        Test de l'ajout d'un acte local avec des données invalides
        """
        commune = self.create_commune()
        response = self.client.post(reverse('communes-membres:admin_acte_add'), {
            'title': '',
            'date': '2023-10-01',
            'description': 'Description de l\'acte',
            'commune': commune.id,
            'file': SimpleUploadedFile(
                name='test_file.pdf',
                content=b'fake_file_content',
                content_type='application/pdf'
            )
        })
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        # Vérifier que l'acte local n'a pas été créé
        self.assertFalse(ActeLocal.objects.filter(title='').exists())
        # Vérifier que le document n'a pas été créé
        self.assertFalse(os.path.exists(os.path.join(MEDIA_ROOT, 'test_file.pdf')))
        # Vérifier le template utilisé
        self.assertTemplateUsed(response, 'communes_membres/admin_acte_add.html')

    # Test de la modification d'un acte local
    def test_update_acte_local(self):
        """
        Test de la modification d'un acte local
        """
        commune = self.create_commune()
        acte_local = self.create_acte_local(commune)
        response = self.client.post(reverse('communes-membres:admin_acte_update', args=[acte_local.id]), {
            'title': 'Test Acte Modifié',
            'date': '2023-10-02',
            'description': 'Description de l\'acte modifié',
            'commune': commune.id,
            'file': SimpleUploadedFile(
                name='test_file_updated.pdf',
                content=b'fake_file_content_updated',
                content_type='application/pdf'
            )
        })
        # Vérifier que la réponse est une redirection
        self.assertEqual(response.status_code, 302)
        # Vérifier que l'utilisateur est redirigé vers la liste des actes locaux
        self.assertRedirects(response, reverse('communes-membres:admin_acte_list'))
        # Vérifier que l'acte local a été mis à jour
        acte_local.refresh_from_db()  # Permet de rafraîchir l'instance depuis la base de données
        self.assertEqual(acte_local.title, 'Test Acte Modifié')
        self.assertEqual(acte_local.description, 'Description de l\'acte modifié')
        # Vérifier que le document a été mis à jour
        self.assertTrue(os.path.exists(
            "test_commune_media/communes/actes_locaux/test_file_updated.pdf"))
        # Vérifier que le document précédent a été supprimé
        self.assertFalse(os.path.exists(
            "test_commune_media/communes/actes_locaux/test_file.pdf"))

    # Test de la modification d'un acte local avec des données invalides
    def test_update_acte_local_invalid_data(self):
        """
        Test de la modification d'un acte local avec des données invalides
        """
        commune = self.create_commune()
        acte_local = self.create_acte_local(commune)
        response = self.client.post(reverse('communes-membres:admin_acte_update', args=[acte_local.id]), {
            'title': '',
            'date': '2023-10-02',
            'description': 'Description de l\'acte modifié',
            'commune': commune.id,
            'file': SimpleUploadedFile(
                name='test_file_updated.pdf',
                content=b'fake_file_content_updated',
                content_type='application/pdf'
            )
        })
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        # Vérifier que l'acte local n'a pas été mis à jour
        acte_local.refresh_from_db()
        # Vérifier que le titre n'a pas été modifié
        self.assertTrue(acte_local.title == 'Test Acte')
        # Vérifier que la description n'a pas été modifiée
        self.assertTrue(acte_local.description == 'Description de l\'acte')
        # Vérifier que le document n'a pas été mis à jour
        self.assertFalse(os.path.exists(
            "test_commune_media/communes/actes_locaux/test_file_updated.pdf"))
        self.assertTrue(os.path.exists(
            "test_commune_media/communes/actes_locaux/test_file.pdf"))

    # Test de la suppression d'un acte local
    def test_delete_acte_local(self):
        """
        Test de la suppression d'un acte local
        """
        commune = self.create_commune()
        acte_local = self.create_acte_local(commune)
        response = self.client.post(
            reverse('communes-membres:admin_acte_delete', args=[acte_local.id]))
        # Vérifier que la réponse est une redirection
        self.assertEqual(response.status_code, 302)
        # Vérifier que l'utilisateur est redirigé vers la liste des actes locaux
        self.assertRedirects(response, reverse('communes-membres:admin_acte_list'))
        # Vérifier que l'acte local a été supprimé
        self.assertFalse(ActeLocal.objects.filter(id=acte_local.id).exists())
        # Vérifier que le document a été supprimé
        self.assertFalse(os.path.exists(
            "test_commune_media/communes/actes_locaux/test_file.pdf"))
