from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.utils import timezone

import os
import shutil
from datetime import timedelta
from PIL import Image
from io import BytesIO


from .models import SemestrielPage, Event
from .forms import SemestrielForm, EventForm

User = get_user_model()
MEDIA_ROOT = 'test_media_semestriel'


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SemestrielPageViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.semestriel_url = reverse('semestriels:semestriel')
        self.today = timezone.now().date()

    def tearDown(self):
        SemestrielPage.objects.all().delete()
        Event.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def test_semestriel_view_get_view(self):
        """Test l'affichage de la page semestriel (GET request)."""
        response = self.client.get(self.semestriel_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'semestriel/semestriel.html')
        self.assertIn('content', response.context)
        self.assertIn('incoming_events', response.context)
        self.assertIn('passed_events', response.context)

    def test_semestriel_view_no_content(self):
        """Test l'affichage de la page semestriel sans contenu."""
        response = self.client.get(self.semestriel_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'semestriel/semestriel.html')
        self.assertIn('content', response.context)
        self.assertIn('incoming_events', response.context)
        self.assertIn('passed_events', response.context)

    def test_semestriel_view_with_content(self):
        """Test l'affichage de la page semestriel avec du contenu."""
        image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        image.save(buffer, format='jpeg')
        valid_image_file = SimpleUploadedFile("test.jpg", buffer.getvalue(), content_type='image/jpeg')
        valid_pdf_file = SimpleUploadedFile("test.pdf", b"This is a test PDF file.", content_type='application/pdf')
        SemestrielPage.objects.create(picture=valid_image_file, file=valid_pdf_file)

        response = self.client.get(self.semestriel_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'semestriel/semestriel.html')
        self.assertIn('content', response.context)
        self.assertIsNotNone(response.context['content'].picture)
        self.assertIsNotNone(response.context['content'].file)
        self.assertIn('incoming_events', response.context)
        self.assertIn('passed_events', response.context)

        if os.path.exists(response.context['content'].picture.path):
            os.remove(response.context['content'].picture.path)
        if os.path.exists(response.context['content'].file.path):
            os.remove(response.context['content'].file.path)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class EventListViewTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(email='admin@example.com', password='password123')
        self.client.login(email='admin@example.com', password='password123')
        self.event_list_url = reverse('semestriels:admin_evenements_list')
        self.today = timezone.now().date()
        Event.objects.create(title="Event 1", start_date=self.today, end_date=self.today + timedelta(days=1), location="Loc 1")
        Event.objects.create(title="Event 2", start_date=self.today + timedelta(days=2), end_date=self.today + timedelta(days=3), location="Loc 2")

    def test_event_list_get_view(self):
        """Test l'affichage de la liste des événements (GET request)."""
        response = self.client.get(self.event_list_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'semestriel/admin_event_list.html')
        self.assertEqual(len(response.context['incoming_events']), 2)
        self.assertEqual(len(response.context['passed_events']), 0)

    def test_event_list_no_events(self):
        """Test l'affichage de la liste des événements lorsqu'il n'y a pas d'événements."""
        Event.objects.all().delete()
        response = self.client.get(self.event_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'semestriel/admin_event_list.html')
        self.assertEqual(response.context['incoming_events'], None)
        self.assertEqual(response.context['passed_events'], None)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AddEventViewTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(email='admin@example.com', password='password123')
        self.client.login(email='admin@example.com', password='password123')
        self.add_event_url = reverse('semestriels:add_event')
        self.event_list_url = reverse('semestriels:admin_evenements_list')
        self.today = timezone.now().date()
        Event.objects.create(title="Event 1", start_date=self.today, end_date=self.today + timedelta(days=1), location="Loc 1")
        Event.objects.create(title="Event 2", start_date=self.today + timedelta(days=2), end_date=self.today + timedelta(days=3), location="Loc 2")

    def tearDown(self):
        Event.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def test_add_event_get_view(self):
        """Test l'affichage du formulaire d'ajout d'événement (GET request)."""
        response = self.client.get(self.add_event_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'semestriel/admin_event_add.html')
        self.assertIsInstance(response.context['form'], EventForm)

    def test_add_event_post_valid_data(self):
        """Test la création d'un événement avec des données valides (POST request)."""
        form_data = {
            'title': 'New Event',
            'start_date': self.today,
            'end_date': self.today + timedelta(days=1),
            'location': 'New Location',
        }
        response = self.client.post(self.add_event_url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 3)  # 2 existing + 1 new
        new_event = Event.objects.last()
        self.assertEqual(new_event.title, 'New Event')
        self.assertRedirects(response, self.event_list_url)

    def test_add_event_post_invalid_data(self):
        """Test l'échec de la création d'un événement avec des données invalides (POST request)."""
        form_data = {
            'title': 'Invalid Event',
            'start_date': self.today + timedelta(days=1),
            'end_date': self.today,
            'location': 'Invalid Location',
        }
        response = self.client.post(self.add_event_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 2)
        self.assertFalse(os.path.exists(os.path.join(MEDIA_ROOT, 'events', 'Invalid Event')))  # Vérifie que l'événement n'a pas été créé

    def test_add_event_post_missing_data(self):
        """Test l'échec de la création d'un événement si des données sont manquantes (POST request)."""
        form_data = {
            'title': '',
            'start_date': self.today,
            'end_date': self.today + timedelta(days=1),
            'location': 'New Location',
        }
        response = self.client.post(self.add_event_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 2)
        self.assertIn('title', response.context['form'].errors)


class EditEventViewTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(email='admin@example.com', password='password123')
        self.client.login(email='admin@example.com', password='password123')
        self.edit_event_url = reverse('semestriels:edit_event', args=[1])
        self.event_list_url = reverse('semestriels:admin_evenements_list')
        self.today = timezone.now().date()
        Event.objects.create(title="Event 1", start_date=self.today, end_date=self.today + timedelta(days=1), location="Loc 1")
        Event.objects.create(title="Event 2", start_date=self.today + timedelta(days=2), end_date=self.today + timedelta(days=3), location="Loc 2")

    def tearDown(self):
        Event.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def test_edit_event_get_view(self):
        """Test l'affichage du formulaire d'édition d'événement (GET request)."""
        event = Event.objects.first()
        response = self.client.get(self.edit_event_url, args=[event.pk])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'semestriel/admin_event_edit.html')
        self.assertIsInstance(response.context['event'], EventForm)
        self.assertEqual(response.context['event'].instance, event)

    def test_edit_event_post_valid_data(self):
        """Test la modification d'un événement avec des données valides (POST request)."""
        event = Event.objects.first()
        form_data = {
            'title': 'Updated Event',
            'start_date': self.today + timedelta(days=1),
            'end_date': self.today + timedelta(days=2),
            'location': 'Updated Location',
        }
        response = self.client.post(self.edit_event_url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        event.refresh_from_db()
        self.assertEqual(event.title, 'Updated Event')
        self.assertEqual(event.location, 'Updated Location')
        self.assertEqual(event.start_date, self.today + timedelta(days=1))
        self.assertRedirects(response, self.event_list_url)

    def test_edit_event_post_invalid_data(self):
        """Test l'échec de la modification d'un événement avec des données invalides (POST request)."""
        event = Event.objects.first()
        form_data = {
            'title': 'Invalid Event',
            'start_date': self.today + timedelta(days=1),
            'end_date': self.today,
            'location': 'Invalid Location',
        }
        response = self.client.post(self.edit_event_url, form_data)
        self.assertEqual(response.status_code, 200)
        event.refresh_from_db()
        self.assertNotEqual(event.title, 'Invalid Event')
        self.assertTrue(event.title == 'Event 1')  # Vérifie que le titre n'a pas été modifié


class DeleteEventViewTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(email='admin@example.com', password='password123')
        self.client.login(email='admin@example.com', password='password123')
        self.delete_event_url = reverse('semestriels:delete_event', args=[1])
        self.event_list_url = reverse('semestriels:admin_evenements_list')
        self.today = timezone.now().date()
        Event.objects.create(title="Event 1", start_date=self.today, end_date=self.today + timedelta(days=1), location="Loc 1")
        Event.objects.create(title="Event 2", start_date=self.today + timedelta(days=2), end_date=self.today + timedelta(days=3), location="Loc 2")

    def tearDown(self):
        Event.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def test_delete_event_get_view(self):
        """Test l'affichage de la page de confirmation de suppression d'événement (GET request)."""
        event = Event.objects.first()
        response = self.client.get(self.delete_event_url, args=[event.pk])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'semestriel/admin_event_delete.html')
        self.assertIsInstance(response.context['event'], Event)
        self.assertEqual(response.context['event'], event)

    def test_delete_event_post_valid_data(self):
        """Test la suppression d'un événement avec des données valides (POST request)."""
        event = Event.objects.first()
        response = self.client.post(self.delete_event_url, args=[event.pk], follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 1)
        self.assertRedirects(response, self.event_list_url)

class AddContentViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(email='admin@example.com', password='password123')

    def setUp(self):
        self.client = Client()
        self.client.login(email='admin@example.com', password='password123')
        self.add_content_url = reverse('semestriels:add_content')

        # Créer des fichiers de test valides
        self.image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        self.image.save(buffer, format='jpeg')
        self.valid_image_file = SimpleUploadedFile("test.jpg", buffer.getvalue(), content_type='image/jpeg')
        self.valid_pdf_file = SimpleUploadedFile("test.pdf", b"This is a test PDF file.", content_type='application/pdf')

        # Créer des fichiers de test invalides
        self.invalid_image_file = SimpleUploadedFile("test.txt", b"This is not an image.", content_type='text/plain')
        self.invalid_pdf_file = SimpleUploadedFile("test.txt", b"This is not a PDF.", content_type='text/plain')
        self.too_large_file = SimpleUploadedFile("large.jpg", b"A" * 2 * 1024 * 1024, content_type='image/jpeg')  # Supposons une limite de 1MB

    def tearDown(self):
        SemestrielPage.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def test_add_content_get_view(self):
        """Test l'affichage du formulaire d'ajout de contenu (GET request)."""
        response = self.client.get(self.add_content_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'semestriel/admin_content_add.html')
        self.assertIsInstance(response.context['form'], SemestrielForm)

    def test_add_content_post_valid_data(self):
        """Test la création de contenu (image et PDF) avec des données valides (POST request)."""
        form_data = {
            'picture': self.valid_image_file,
            'file': self.valid_pdf_file,
        }
        response = self.client.post(self.add_content_url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SemestrielPage.objects.count(), 1)
        new_content = SemestrielPage.objects.first()
        self.assertIsNotNone(new_content.picture)
        self.assertIsNotNone(new_content.file)
        self.assertRedirects(response, reverse('semestriels:admin_evenements_list'))

        # Nettoyer les fichiers créés lors du test
        if new_content.picture:
            os.remove(new_content.picture.path)
        if new_content.file:
            os.remove(new_content.file.path)

    def test_add_content_post_invalid_image_type(self):
        """Test l'échec de la création avec un type de fichier image invalide."""
        form_data = {
            'picture': self.invalid_image_file,
            'file': self.valid_pdf_file,
        }
        response = self.client.post(self.add_content_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SemestrielPage.objects.count(), 0)
        self.assertIn('picture', response.context['form'].errors)

    def test_add_content_post_invalid_pdf_type(self):
        """Test l'échec de la création avec un type de fichier PDF invalide."""
        form_data = {
            'picture': self.valid_image_file,
            'file': self.invalid_pdf_file,
        }
        response = self.client.post(self.add_content_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SemestrielPage.objects.count(), 0)
        self.assertIn('file', response.context['form'].errors)

    def test_add_content_post_missing_files(self):
        """Test l'échec de la création si des fichiers sont manquants (si les champs sont requis dans le formulaire)."""
        form_data = {}
        response = self.client.post(self.add_content_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SemestrielPage.objects.count(), 0)
        if 'picture' in response.context['form'].errors:
            self.assertIn('picture', response.context['form'].errors)
        if 'file' in response.context['form'].errors:
            self.assertIn('file', response.context['form'].errors)

    # Ajouter un test pour la validation de la taille du fichier si vous l'avez implémentée dans le formulaire
    # Exemple (en supposant une limite de 1MB):
    def test_add_content_post_image_too_large(self):
        """Test l'échec de la création si la taille de l'image est trop grande."""
        form_data = {
            'picture': self.too_large_file,
            'file': self.valid_pdf_file,
        }
        response = self.client.post(self.add_content_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SemestrielPage.objects.count(), 0)
        self.assertIn('picture', response.context['form'].errors)

    def test_add_content_post_creates_only_one_instance(self):
        """Test que seule une instance de SemestrielPage existe après la création."""
        SemestrielPage.objects.create(picture=self.valid_image_file, file=self.valid_pdf_file)
        self.assertEqual(SemestrielPage.objects.count(), 1) # Vérifie qu'il y a déjà une instance

        form_data = {
            'picture': self.valid_image_file,
            'file': self.valid_pdf_file,
        }
        response = self.client.post(self.add_content_url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SemestrielPage.objects.count(), 1) # Doit toujours y avoir une seule instance

        # Vérifier que les anciens fichiers ont été supprimés (impliqué par la logique save())
        new_content = SemestrielPage.objects.first()
        self.assertIsNotNone(new_content.picture)
        self.assertIsNotNone(new_content.file)

        # Nettoyer les fichiers
        if new_content.picture:
            os.remove(new_content.picture.path)
        if new_content.file:
            os.remove(new_content.file.path)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class EditContentViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.superuser = User.objects.create_superuser(email='admin@example.com', password='password123')

    def setUp(self):
        self.client = Client()
        self.client.login(email='admin@example.com', password='password123')

        # Créer un contenu semestriel existant pour l'édition
        self.image = Image.new('RGB', (50, 50), color='blue')
        buffer = BytesIO()
        self.image.save(buffer, format='jpeg')
        self.existing_image_file = SimpleUploadedFile("existing.jpg", buffer.getvalue(), content_type='image/jpeg')
        self.existing_pdf_file = SimpleUploadedFile("existing.pdf", b"Existing PDF content.", content_type='application/pdf')
        self.existing_content = SemestrielPage.objects.create(picture=self.existing_image_file, file=self.existing_pdf_file)
        self.edit_content_url = reverse('semestriels:edit_content',
                                            args=[self.existing_content.pk])

        # Créer des fichiers valides pour la modification
        self.new_image = Image.new('RGB', (100, 100), color='red')
        new_buffer = BytesIO()
        self.new_image.save(new_buffer, format='jpeg')
        self.new_image_file = SimpleUploadedFile("new.jpg", new_buffer.getvalue(), content_type='image/jpeg')
        self.new_pdf_file = SimpleUploadedFile("new.pdf", b"New PDF content.", content_type='application/pdf')

    def tearDown(self):
        SemestrielPage.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    def test_edit_content_get_view(self):
        """Test l'affichage du formulaire d'édition de contenu (GET request)."""
        response = self.client.get(self.edit_content_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'semestriel/admin_content_edit.html')
        self.assertIsInstance(response.context['form'], SemestrielForm)
        self.assertEqual(response.context['form'].instance, self.existing_content)

    def test_edit_content_post_valid_data(self):
        """Test la modification du contenu (image et PDF) avec des données valides (POST request)."""
        original_image_path = self.existing_content.picture.path
        original_file_path = self.existing_content.file.path

        form_data = {
            'picture': self.new_image_file,
            'file': self.new_pdf_file,
        }
        response = self.client.post(self.edit_content_url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.existing_content.refresh_from_db()
        self.assertIsNotNone(self.existing_content.picture)
        self.assertIsNotNone(self.existing_content.file)
        self.assertNotEqual(self.existing_content.picture.path, original_image_path)
        self.assertNotEqual(self.existing_content.file.path, original_file_path)
        self.assertRedirects(response, reverse('semestriels:admin_evenements_list'))

        # Nettoyer les fichiers
        if os.path.exists(self.existing_content.picture.path):
            os.remove(self.existing_content.picture.path)
        if os.path.exists(self.existing_content.file.path):
            os.remove(self.existing_content.file.path)

    def test_edit_content_post_valid_data_no_file_change(self):
        """Test la modification sans changer les fichiers (POST request)."""
        original_image_name = self.existing_content.picture.name
        original_file_name = self.existing_content.file.name

        form_data = {
            'picture': original_image_name,
            'file': original_file_name,
        }
        response = self.client.post(self.edit_content_url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.existing_content.refresh_from_db()
        self.assertEqual(self.existing_content.picture.name, original_image_name)
        self.assertEqual(self.existing_content.file.name, original_file_name)
        self.assertRedirects(response, reverse('semestriels:admin_evenements_list'))
