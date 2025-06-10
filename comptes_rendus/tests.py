from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.urls import reverse
from django.test import Client
from comptes_rendus.models import CompteRendu, Conseil
import os, shutil
from django.core.files.uploadedfile import SimpleUploadedFile



User = get_user_model()
MEDIA_ROOT = 'test_media_comptes-rendus'

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ComptesRendusTestCase(TestCase):
    """
    Tests pour les vues de l'application Comptes Rendus.
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

    def tearDown(self):
        CompteRendu.objects.all().delete()
        Conseil.objects.all().delete()
        # Supprimer le répertoire MEDIA_ROOT après les tests
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    # Test d'affichage de la page publique
    def test_cr_public_get_views(self):
        """
        Test de la page publique des comptes-rendus.
        """
        response = self.client.get(reverse('comptes_rendus:comptes_rendus'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comptes_rendus/comptes-rendus.html')
        self.assertContains(response, "Non disponible.")
        self.assertContains(response, "Aucun conseil disponible")

    def test_cr_public_get_views_with_data(self):
        """
        Test de la page publique des comptes-rendus avec des données.
        """
        compte_rendu = CompteRendu.objects.create(link="https://example.com/cr")
        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=None
        )

        response = self.client.get(reverse('comptes_rendus:comptes_rendus'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comptes_rendus/comptes-rendus.html')
        self.assertContains(response, "https://example.com/cr")
        self.assertContains(response, "10h00")
        self.assertContains(response, "Salle de réunion")
        self.assertContains(response, "À venir")
        self.assertContains(response, "1 octobre 2023")

    # Test de la page admin
    def test_cr_admin_get_views(self):
        """
        Test de la page admin des comptes-rendus.
        """
        response = self.client.get(reverse('comptes_rendus:admin_cr_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comptes_rendus/admin_page.html')
        self.assertContains(response, "Ajouter le lien vers les comptes rendus")
        self.assertContains(response, "Programmer un conseil")
        self.assertContains(response, "Aucun compte rendu disponible")
    
    def test_cr_admin_get_views_with_data(self):
        """
        Test de la page admin des comptes-rendus avec des données.
        """
        compte_rendu = CompteRendu.objects.create(link="https://example.com/cr")
        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=None
        )

        response = self.client.get(reverse('comptes_rendus:admin_cr_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comptes_rendus/admin_page.html')
        self.assertContains(response, "https://example.com/cr")
        self.assertContains(response, "10h00")
        self.assertContains(response, "Salle de réunion")
        self.assertContains(response, "À venir")
        self.assertContains(response, "1 octobre 2023")

    # Test d'ajout des conseils
    def test_cr_admin_add_conseil_get_view(self):
        """
        Test de la page d'ajout d'un conseil.
        """
        response = self.client.get(reverse('comptes_rendus:add_conseil'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comptes_rendus/admin_conseil_add.html')
        self.assertContains(response, "Publier")
        self.assertContains(response, "Date")
        self.assertContains(response, "Heure")
        self.assertContains(response, "Lieu")
        self.assertContains(response, "Ordre du jour")

    def test_cr_admin_add_conseil_post_view(self):
        """
        Test de l'ajout d'un conseil.
        """

        response = self.client.post(reverse('comptes_rendus:add_conseil'), {
            'date': '2023-10-01',
            'hour': '10:00',
            'place': 'Salle de réunion',
            'day_order': SimpleUploadedFile('test.pdf', content=b"Document pdf de test", content_type='application/pdf'),
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Conseil.objects.filter(date='2023-10-01').exists())


    def test_cr_admin_add_conseil_post_view_without_file(self):
        """
        Test de l'ajout d'un conseil sans fichier.
        """
        response = self.client.post(reverse('comptes_rendus:add_conseil'), {
            'date': '2023-10-01',
            'hour': '10:00',
            'place': 'Salle de réunion',
            'day_order': '',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Conseil.objects.filter(date='2023-10-01').exists())

    def test_cr_admin_add_conseil_post_view_invalid_data(self):
        """
        Test de l'ajout d'un conseil avec des données invalides.
        """
        response = self.client.post(reverse('comptes_rendus:add_conseil'), {
            'date': '2023-10-01',
            'hour': '10:00',
            'place': '',
            'day_order': SimpleUploadedFile('test.pdf', content=b"Document pdf de test", content_type='application/pdf'),
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comptes_rendus/admin_conseil_add.html')
        self.assertFalse(Conseil.objects.filter(date='2023-10-01').exists())
        self.assertFalse(os.path.exists(MEDIA_ROOT + '/comptes-rendus/ordre-du-jour/pdf_1.pdf'))

    # Test de la page d'édition des conseils
    def test_cr_admin_edit_conseil_get_view(self):
        """
        Test de la page d'édition d'un conseil.
        """
        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=None
        )
        response = self.client.get(reverse('comptes_rendus:edit_conseil', args=[conseil.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comptes_rendus/admin_conseil_edit.html')
        self.assertContains(response, "Appliquer")
    
    def test_cr_admin_edit_conseil_post_view(self):
        """
        Test de l'édition d'un conseil.
        """

        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=SimpleUploadedFile('last_day_order.pdf', content=b"Document pdf de test", content_type='application/pdf'),
        )

        id = conseil.id
        last_day_order_path = conseil.day_order.path

        response = self.client.post(reverse('comptes_rendus:edit_conseil', args=[conseil.id]), {
            'date': '2023-10-02',
            'hour': '11:00',
            'place': 'Salle de réunion 2',
            'day_order': SimpleUploadedFile('new_day_order.pdf', content=b"Document pdf de test", content_type='application/pdf'),
        })

        # on récupère le conseil mis à jour
        conseil = Conseil.objects.get(id=id)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(os.path.exists(last_day_order_path))
        self.assertTrue(os.path.exists(conseil.day_order.path))
        self.assertTrue(Conseil.objects.filter(date='2023-10-02').exists())
        self.assertFalse(Conseil.objects.filter(date='2023-10-01').exists())

    def test_cr_admin_edit_conseil_post_view_without_file(self):
        """
        Test de l'édition d'un conseil sans fichier changement de fichier.
        """

        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=SimpleUploadedFile('last_day_order.pdf', content=b"Document pdf de test", content_type='application/pdf'),
        )

        id = conseil.id
        last_day_order_path = conseil.day_order.path

        response = self.client.post(reverse('comptes_rendus:edit_conseil', args=[conseil.id]), {
            'date': '2023-10-02',
            'hour': '11:00',
            'place': 'Salle de réunion 2',
            'day_order': '',
        })

        # on récupère le conseil mis à jour
        conseil = Conseil.objects.get(id=id)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(os.path.exists(last_day_order_path))
        self.assertTrue(Conseil.objects.filter(date='2023-10-02').exists())
        self.assertFalse(Conseil.objects.filter(date='2023-10-01').exists())

    def test_cr_admin_edit_conseil_post_view_invalid_data(self):
        """
        Test de l'édition d'un conseil avec des données invalides.
        """
        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=SimpleUploadedFile('last_day_order.pdf', content=b"Document pdf de test", content_type='application/pdf'),
        )

        id = conseil.id
        last_day_order_path = conseil.day_order.path

        response = self.client.post(reverse('comptes_rendus:edit_conseil', args=[conseil.id]), {
            'date': '2023-10-02',
            'hour': '11:00',
            'place': '',
            'day_order': SimpleUploadedFile('new_day_order.pdf', content=b"Document pdf de test", content_type='application/pdf'),
        })

        # on récupère le conseil mis à jour
        conseil = Conseil.objects.get(id=id)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comptes_rendus/admin_conseil_edit.html')
        self.assertTrue(os.path.exists(last_day_order_path))


    # Test de la page de suppression des conseils
    def test_cr_admin_delete_conseil_get_view(self):
        """
        Test de la page de suppression d'un conseil.
        """
        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=SimpleUploadedFile('not_deleted_day_order.pdf', content=b"Document pdf de test", content_type='application/pdf'),
        )
        response = self.client.get(reverse('comptes_rendus:delete_conseil', args=[conseil.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'comptes_rendus/admin_conseil_delete.html')
        self.assertContains(response, "Supprimer le conseil")

    def test_cr_admin_delete_conseil_post_view(self):
        """
        Test de la suppression d'un conseil.
        """
        conseil = Conseil.objects.create(
            date="2023-10-01",
            hour="10:00",
            place="Salle de réunion",
            day_order=SimpleUploadedFile('day_order_to_delete.pdf', content=b"Document pdf de test", content_type='application/pdf'),
        )

        id = conseil.id
        day_order_path = conseil.day_order.path

        response = self.client.post(reverse('comptes_rendus:delete_conseil', args=[conseil.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Conseil.objects.filter(id=id).exists())
        self.assertFalse(os.path.exists(day_order_path))