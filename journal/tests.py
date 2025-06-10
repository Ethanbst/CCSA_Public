from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib import messages
from io import BytesIO
from PIL import Image
import os
import shutil
from .models import Journal
from datetime import date
from .forms import JournalForm

User = get_user_model()  # Récupérer le modèle d'utilisateur personnalisé

# Définir un répertoire temporaire pour les médias
MEDIA_ROOT = 'test_media'


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class JournalAddJournalViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un superutilisateur personnalisé
        # print("Création du super_user\n")
        cls.superuser = User.objects.create_superuser(
            email='admin@example.com',  # Utiliser l'email comme nom d'utilisateur
            password='password123'
        )

    def setUp(self):
        self.client = Client()
        self.client.login(email='admin@example.com', password='password123')  # Se connecter avec l'email
        self.add_journal_url = reverse('journal:add_journal')

        # Créer des fichiers de test (factices)
        self.document_content = b"This is a test document."
        self.document_file = SimpleUploadedFile("test.pdf", self.document_content, content_type="application/pdf")

        self.image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        self.image.save(buffer, format='jpeg')
        self.image_content = buffer.getvalue()
        self.cover_file = SimpleUploadedFile("test.jpg", self.image_content, content_type="image/jpeg")

    def tearDown(self):
        # Nettoyer les fichiers uploadés après chaque test
        Journal.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)  # Supprimer le répertoire et son contenu

    def test_add_journal_get_view(self):
        """
        Test l'affichage du formulaire d'ajout de journal (GET request).
        """
        response = self.client.get(self.add_journal_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'journal/add_journal.html')
        self.assertIsInstance(response.context['journal'], JournalForm)

    def test_add_journal_post_valid_data(self):
        """
        Test la création d'un journal avec des données valides (POST request).
        """
        form_data = {
            'title': 'New Valid Journal',
            'document': self.document_file,
            'cover': self.cover_file,
            'number': 10,
            'release_date': date(2024, 1, 1),
            'page_number': 25,
        }

        response = self.client.post(self.add_journal_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Journal.objects.count(), 1)

        new_journal = Journal.objects.first()
        self.assertEqual(new_journal.title, 'New Valid Journal')
        self.assertEqual(new_journal.number, 10)
        self.assertEqual(new_journal.page_number, 25)
        self.assertEqual(new_journal.release_date, date(2024, 1, 1))

        # Vérifier le message de succès
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Le journal a été ajouté avec succès.")
        self.assertRedirects(response, reverse('journal:admin_journaux_list'))

    def test_add_journal_post_invalid_data(self):
        """
        Test la non-création d'un journal avec des données invalides (POST request).
        """
        response = self.client.post(self.add_journal_url, {
            'title': '',  # Champ requis manquant
            'number': 'abc', # Mauvais type
            'release_date': 'invalid-date',
            'page_number': -5,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Journal.objects.count(), 0)
        self.assertTemplateUsed(response, 'journal/add_journal.html')

        # Vérifier le message d'erreur
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Merci de corriger les erreurs dans le formulaire.")

    def test_add_journal_post_missing_files(self):
        """
        Test la non-création si les fichiers 'document' ou 'cover' sont manquants.
        """
        response = self.client.post(self.add_journal_url, {
            'title': 'Missing Files Journal',
            'number': 11,
            'release_date': date(2024, 1, 1),
            'page_number': 26,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Journal.objects.count(), 0)
        self.assertTemplateUsed(response, 'journal/add_journal.html')
        self.assertIn('document', response.context['journal'].errors)
        self.assertIn('cover', response.context['journal'].errors)

    def test_add_journal_post_invalid_file_types(self):
        """
        Test la non-création si les types de fichiers sont invalides.
        """
        invalid_document = SimpleUploadedFile("test.txt", b"Invalid content", content_type="text/plain")
        invalid_cover = SimpleUploadedFile("test.gif", b"Invalid content", content_type="image/gif")

        response = self.client.post(self.add_journal_url, {
            'title': 'Invalid Files Journal',
            'number': 12,
            'release_date': date(2024, 1, 1),
            'page_number': 27,
            'document': invalid_document,
            'cover': invalid_cover,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Journal.objects.count(), 0)
        self.assertTemplateUsed(response, 'journal/add_journal.html')
        self.assertIn('document', response.context['journal'].errors)
        self.assertIn('cover', response.context['journal'].errors)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class JournalEditJournalViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un superutilisateur personnalisé
        cls.superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='password123'
        )

    def setUp(self):
        # print("Connexion avec le compte super_user\n")
        self.client = Client()
        self.client.login(email='admin@example.com', password='password123')
        self.journal = Journal.objects.create(
            title='Original Journal',
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10
        )
        self.edit_journal_url = reverse('journal:edit_journal', args=[self.journal.id])

        # Créer des fichiers de test (factices) - Réutilisable
        # print("Création de fichiers de test\n")
        self.document_content = b"This is a test document."
        self.document_file = SimpleUploadedFile("test.pdf", self.document_content, content_type="application/pdf")

        # Créer un fichier image de test
        self.image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        self.image.save(buffer, format='jpeg')
        self.image_content = buffer.getvalue()
        self.cover_file = SimpleUploadedFile("test.jpg", self.image_content, content_type="image/jpeg")

    def tearDown(self):
        # Nettoyer les fichiers uploadés après chaque test
        # print("Nettoyage des fichiers de test\n")
        Journal.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)  # Supprimer le répertoire et son contenu

    def test_edit_journal_get_view(self):
        """
        Test l'affichage du formulaire d'édition de journal (GET request).
        """
        # print("Test d'affichage du formulaire d'édition de journal\n")
        response = self.client.get(self.edit_journal_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'journal/edit_journal.html')
        self.assertIsInstance(response.context['journal'], JournalForm)
        self.assertEqual(response.context['journal'].instance, self.journal)

    def test_edit_journal_post_valid_data(self):
        """
        Test la modification d'un journal avec des données valides (POST request).
        """
        # print("Test de modification d'un journal avec données valides\n")
        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()
        original_document_path = self.journal.document.path
        original_cover_path = self.journal.cover.path

        # Créer de nouveaux fichiers pour la mise à jour
        new_document_content = b"This is an updated document."
        new_document_file = SimpleUploadedFile("updated.pdf", new_document_content, content_type="application/pdf")
        new_image = Image.new('RGB', (50, 50), color='blue')
        new_buffer = BytesIO()
        new_image.save(new_buffer, format='jpeg')
        new_cover_file = SimpleUploadedFile("updated.jpg", new_buffer.getvalue(), content_type="image/jpeg")

        form_data = {
            'title': 'Updated Journal',
            'document': new_document_file,
            'cover': new_cover_file,
            'number': 2,
            'release_date': date(2024, 2, 1),
            'page_number': 20,
        }

        response = self.client.post(self.edit_journal_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('journal:admin_journaux_list'))

        # Vérifier que le journal a été mis à jour
        updated_journal = Journal.objects.get(id=self.journal.id)
        self.assertEqual(updated_journal.title, 'Updated Journal')
        self.assertEqual(updated_journal.number, 2)
        self.assertEqual(updated_journal.release_date, date(2024, 2, 1))
        self.assertEqual(updated_journal.page_number, 20)

        # Vérifier que les anciens fichiers ont été supprimés et les nouveaux créés
        self.assertFalse(os.path.exists(original_document_path))
        self.assertFalse(os.path.exists(original_cover_path))
        self.assertTrue(os.path.exists(updated_journal.document.path))
        self.assertTrue(os.path.exists(updated_journal.cover.path))

        # Vérifier le message de succès
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Le journal a été modifié avec succès.")

    def test_edit_journal_post_invalid_data(self):
        """
        Test la non-modification d'un journal avec des données invalides (POST request).
        """
        # print("Test de non modification d'un journal avec données invalides\n")
        response = self.client.post(self.edit_journal_url, {
            'title': '',  # Champ requis manquant
            'number': 'abc',
            'release_date': 'invalid-date',
            'page_number': -5,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'journal/edit_journal.html')

        # Vérifier que le journal n'a pas été modifié
        updated_journal = Journal.objects.get(id=self.journal.id)
        self.assertEqual(updated_journal.title, 'Original Journal')  # Reste inchangé
        self.assertEqual(updated_journal.number, 1)

        # Vérifier le message d'erreur
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Merci de corriger les erreurs dans le formulaire.")

    def test_edit_journal_post_no_file_change(self):
        """
        Test la modification d'un journal sans changer les fichiers (POST request).
        """
        # print("Test de modification d'un journal sans changer les fichiers\n")

        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()

        form_data = {
            'title': 'Updated Title Only',
            'number': 2,
            'release_date': date(2024, 2, 1),
            'page_number': 20,
            'document': self.journal.document.name,  # Passer le nom du fichier existant
            'cover': self.journal.cover.name,
        }

        response = self.client.post(self.edit_journal_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('journal:admin_journaux_list'))

        # Vérifier que le journal a été mis à jour
        updated_journal = Journal.objects.get(id=self.journal.id)
        self.assertEqual(updated_journal.title, 'Updated Title Only')
        self.assertEqual(updated_journal.number, 2)

        # Vérifier que les fichiers n'ont pas été modifiés/supprimés
        self.assertTrue(os.path.exists(updated_journal.document.path))
        self.assertTrue(os.path.exists(updated_journal.cover.path))

        # Vérifier le message de succès
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Le journal a été modifié avec succès.")


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class JournalDeleteJournalViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un superutilisateur personnalisé
        # print("Création du super_user\n")
        cls.superuser = User.objects.create_superuser(email='admin@example.com',
                                                      password='password123')

    def setUp(self):
        # print("Connexion avec le compte super_user\n")
        self.client = Client()
        self.client.login(email='admin@example.com', password='password123')
        self.journal = Journal.objects.create(
            title='Journal to Delete',
            number=1,
            release_date=date(2024, 1, 1),
            page_number=10
        )
        self.delete_journal_url = reverse('journal:delete_journal',
                                          args=[self.journal.id])

        # Créer des fichiers de test (factices) - Réutilisable
        # print("Création de fichiers de test\n")
        self.document_content = b"This is a test document."
        self.document_file = SimpleUploadedFile("test.pdf", self.document_content,
                                                content_type="application/pdf")

        # Créer un fichier image de test
        self.image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        self.image.save(buffer, format='jpeg')
        self.image_content = buffer.getvalue()
        self.cover_file = SimpleUploadedFile("test.jpg", self.image_content,
                                             content_type="image/jpeg")

    def tearDown(self):
        # Nettoyer les fichiers uploadés après chaque test
        # print("Nettoyage des fichiers de test\n")
        Journal.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            # Supprimer le répertoire et son contenu
            shutil.rmtree(MEDIA_ROOT)

    def test_delete_journal_get_view(self):
        """
        Test l'affichage de la page de confirmation de suppression (GET request).
        """
        # print("Test d'affichage de la page de confirmation de suppression\n")

        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()

        response = self.client.get(self.delete_journal_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'journal/delete_journal.html')
        self.assertEqual(response.context['journal'], self.journal)
        self.assertContains(response, "Êtes-vous sûr de vouloir supprimer le journal ?")

    def test_delete_journal_post_confirm(self):
        """
        Test la suppression d'un journal avec confirmation (POST request).
        """
        # print("Test de suppression d'un journal avec confirmation\n")

        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()

        response = self.client.post(self.delete_journal_url, {'confirm': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('journal:admin_journaux_list'))
        self.assertEqual(Journal.objects.count(), 0)

        # Vérifier que les fichiers ont été supprimés
        self.assertFalse(os.path.exists(self.journal.document.path))
        self.assertFalse(os.path.exists(self.journal.cover.path))

        # Vérifier le message de succès
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "Le journal a été supprimé avec succès.")

    def test_delete_journal_post_cancel(self):
        """
        Test d'annulation de la suppression d'un journal (POST request).
        """
        # print("Test d'annulation de suppression d'un journal\n")
        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()

        response = self.client.post(self.delete_journal_url, {'confirm': 'no'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('journal:admin_journaux_list'))
        self.assertEqual(Journal.objects.count(), 1)

        self.assertTrue(os.path.exists(self.journal.document.path))
        self.assertTrue(os.path.exists(self.journal.cover.path))

        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)

    def test_delete_journal_post_no_confirmation(self):
        """
        Test de la non-suppression d'un journal sans confirmation (POST request).
        """
        # print("Test de non suppression d'un journal sans confirmation\n")
        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()

        response = self.client.post(self.delete_journal_url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('journal:admin_journaux_list'))
        self.assertEqual(Journal.objects.count(), 1)

        # Vérifier que les fichiers n'ont pas été supprimés
        self.assertTrue(os.path.exists(self.journal.document.path))
        self.assertTrue(os.path.exists(self.journal.cover.path))

        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)

    def test_delete_journal_post_invalid_confirmation(self):
        """
        Test de la non-suppression d'un journal avec une confirmation invalide (POST request).
        """
        # print("Test de non suppression d'un journal avec confirmation invalide\n")
        # Ajouter des fichiers initiaux au journal
        self.journal.document = self.document_file
        self.journal.cover = self.cover_file
        self.journal.save()

        response = self.client.post(self.delete_journal_url, {'confirm': 'invalid'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('journal:admin_journaux_list'))
        self.assertEqual(Journal.objects.count(), 1)

        # Vérifier que les fichiers n'ont pas été supprimés
        self.assertTrue(os.path.exists(self.journal.document.path))
        self.assertTrue(os.path.exists(self.journal.cover.path))

        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)