from django.test import TestCase
from django.urls import reverse
from .models import *
from conseil_communautaire.models import ConseilVille
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.test import override_settings
import os
import shutil
import io
from PIL import Image

User = get_user_model()

MEDIA_ROOT = 'test_media_bureau_communautaire'

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class BureauCommunautaireTestCase(TestCase):
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
        self.client.login(email='admin@example.com', password='password123')  # Se connecter avec l'email
        self.valid_president_data = {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'rank': 0,
            'role': Elus.Role.PRESIDENT,
            'function': 'Maire de Fourmies',
            'picture': SimpleUploadedFile(
                name='test_image.jpg',
                content=self.generate_test_image('test_image.jpg', 'jpeg').read(),
                content_type='image/jpeg'
            ),
            'city': self.create_city("Fourmies").id,
            'profession': "Maire de Fourmies",
        }

        self.valid_vice_president_data = {
            'first_name': 'Marie',
            'last_name': 'Martin',
            'rank': 1,
            'role': Elus.Role.VICE_PRESIDENT,
            'function': 'Maire de Anor',
            'picture': SimpleUploadedFile(
                name='test_image.jpg',
                content=self.generate_test_image('test_image.jpg', 'jpeg').read(),
                content_type='image/jpeg'
            ),
            'city': self.create_city("Anor").id,
            'profession': "Maire de Anor",
        }

    def tearDown(self):
        # Nettoyer les fichiers uploadés après chaque test
        Elus.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    # Crée une ville avec les informations fournies.
    def create_city(self, nom_commune):
        """
        Crée une ville avec les informations fournies.
        :param nom_commune: Le nom de la commune
        :return: L'objet ConseilVille créé
        """
        return ConseilVille.objects.create(
            city_name=nom_commune,
            mayor_sex="M",
            mayor_first_name="Jean",
            mayor_last_name="Dupont",
            address="1 rue de la Mairie",
            postal_code="59610",
            phone_number="0321234567",
            website="http://www.fourmies.fr",
            image=SimpleUploadedFile(
                name='test_image.jpg',
                content=b'fake_image_content',
                content_type='image/jpeg'
            ),
            slogan="La ville de Fourmies, c'est la vie !",
            nb_habitants="10000",
        )

    # Crée un président avec les informations fournies.
    def create_President(self, nom, prenom):
        """
        Crée un président avec les informations fournies.
        :param nom: Le nom du président
        :param prenom: Le prénom du président
        :return: L'objet Elus créé
        """
        return Elus.objects.create(
            first_name=prenom,
            last_name=nom,
            rank="0",
            role=Elus.Role.PRESIDENT,
            function="RH, TRI",
            picture=SimpleUploadedFile(
                name='test_image.jpg',
                content=b'fake_image_content',
                content_type='image/jpeg'
            ),
            city=ConseilVille.objects.get(city_name="Fourmies"),
            profession="Maire de Fourmies",
        )
    
    # Crée un vice-président avec les informations fournies.
    def create_VicePresident(self, nom, prenom):
        return Elus.objects.create(
            first_name=prenom,
            last_name=nom,
            rank="1",
            role=Elus.Role.VICE_PRESIDENT,
            function="RH, TRI",
            picture=SimpleUploadedFile(
                name='test_image.jpg',
                content=b'fake_image_content',
                content_type='image/jpeg'
        ),
        city=ConseilVille.objects.get(city_name="Anor"),
        profession="Maire de Anor",
    )

    # Créé une image de test pour les tests unitaires
    def generate_test_image(self, name, format):
        """
        Génère une image de test pour les tests unitaires.
        :param name: Le nom de l'image
        :return: Un fichier d'image SimpleUploadedFile
        """
        file = io.BytesIO()
        if format.lower() == 'jpeg' or format.lower() == 'jpg':
            image = Image.new('RGB', size=(100, 100), color=(155, 0, 0))
        else:
            image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, format=format)
        file.name = name
        file.seek(0)
        return file    

    # ----------------------------------------------------------
    # Test des vues d'affichage (get) avec et sans données
    # ----------------------------------------------------------

    # Test de la vue d'accueil publique sans données
    def test_views_get_without_data(self):
        """
        Test de la vue de la page d'accueil sans données
        """
        response = self.client.get(reverse('bureau-communautaire:elus'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bureau_communautaire/elus.html')
        self.assertContains(response, "Découvrez les élus qui œuvrent pour le développement et l'avenir du Sud Avesnois")
        self.assertContains(response, "Aucun président élu")
        self.assertContains(response, "Aucun vice-président élu")
        self.assertContains(response, "Aucun document trouvé")

    # Test de la vue d'accueil publique avec des données
    def test_views_get_with_data(self):
        """
        Test de la vue de la page d'accueil avec des données
        """
        self.create_President("Dupont", "Jean")
        self.create_VicePresident("Martin", "Marie")

        response = self.client.get(reverse('bureau-communautaire:elus'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bureau_communautaire/elus.html')
        self.assertContains(response, "Découvrez les élus qui œuvrent pour le développement et l'avenir du Sud Avesnois")
        self.assertContains(response, "Président")
        self.assertContains(response, "Dupont")
        self.assertContains(response, "Jean")
        self.assertContains(response, "Maire de Fourmies")
        self.assertContains(response, "Vice-Président")
        self.assertContains(response, "Martin")
        self.assertContains(response, "Marie")
        self.assertContains(response, "Maire de Anor")
        self.assertContains(response, "Aucun document trouvé")

    # Test de la vue d'accueil admin sans données
    def test_views_admin_get_without_data(self):
        """
        Test de la vue admin sans données
        """
        response = self.client.get(reverse('bureau-communautaire:admin_elus_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bureau_communautaire/admin_elus_list.html')
        self.assertContains(response, "Liste des élus")
        self.assertContains(response, "Aucun élu trouvé.")
        self.assertContains(response, "Ajouter un élu")

    # Test de la vue d'accueil admin avec des données
    def test_views_admin_get_with_data(self):
        """
        Test de la vue admin avec des données
        """
        self.create_President("Dupont", "Jean")
        self.create_VicePresident("Martin", "Marie")

        response = self.client.get(reverse('bureau-communautaire:admin_elus_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bureau_communautaire/admin_elus_list.html')
        self.assertContains(response, "Liste des élus")
        self.assertContains(response, "Président")
        self.assertContains(response, "Jean")
        self.assertContains(response, "Dupont")
        self.assertContains(response, "Maire de Fourmies")
        self.assertContains(response, "Vice-Président")
        self.assertContains(response, "Marie")
        self.assertContains(response, "Martin")
        self.assertContains(response, "Maire de Anor")

    # ----------------------------------------------------------
    # Test des vues d'ajout (post) avec données valides
    # ----------------------------------------------------------

    # Test de la vue d'ajout d'un élu avec des données valides
    def test_views_add_elus_valid_data(self):
        """
        Test de la vue d'ajout d'un élu avec des données valides
        """
        response = self.client.post(reverse('bureau-communautaire:admin_elu_add'), self.valid_president_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('bureau-communautaire:admin_elus_list'))
        self.assertTrue(Elus.objects.filter(first_name='Jean', last_name='Dupont').exists())
        self.assertContains(response, "Jean")
        self.assertContains(response, "Dupont")
        self.assertContains(response, "Maire de Fourmies")

# ----------------------------------------------------------
# Test des vues d'ajout (post) avec données invalides pour chaque champs
# ----------------------------------------------------------
@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class EluFormFieldRequiredTests(TestCase):
    """
    Teste les champs obligatoires (ou non) du formulaire d'ajout d'un élu.
    À utiliser dans une classe de test héritant de BureauCommunautaireTestCase.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un superutilisateur personnalisé
        cls.superuser = User.objects.create_superuser(
            email='admin@example.com',  # Utiliser l'email comme nom d'utilisateur
            password='password123'
        )
        cls.client = Client()

    def setUp(self):
        return BureauCommunautaireTestCase.setUp(self)

    def tearDown(self):
        return BureauCommunautaireTestCase.tearDown(self)

    def create_city(self, nom_commune):
        return BureauCommunautaireTestCase.create_city(self, nom_commune)

    def create_President(self, nom, prenom):
        return BureauCommunautaireTestCase.create_President(self, nom, prenom)

    def create_VicePresident(self, nom, prenom):
        return BureauCommunautaireTestCase.create_VicePresident(self, nom, prenom)

    def generate_test_image(self, name, format):
        return BureauCommunautaireTestCase.generate_test_image(self, name, format) 


    def test_first_name_required(self):
        data = self.valid_president_data.copy()
        data['first_name'] = ''
        response = self.client.post(reverse('bureau-communautaire:admin_elu_add'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context['elu_form']
        self.assertTrue(form.errors['first_name'])
        self.assertIn('Ce champ est obligatoire.', form.errors['first_name'])

    def test_last_name_required(self):
        data = self.valid_president_data.copy()
        data['last_name'] = ''
        response = self.client.post(reverse('bureau-communautaire:admin_elu_add'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context['elu_form']
        self.assertTrue(form.errors['last_name'])
        self.assertIn('Ce champ est obligatoire.', form.errors['last_name'])

    def test_rank_required(self):
        data = self.valid_president_data.copy()
        data['rank'] = ''
        response = self.client.post(reverse('bureau-communautaire:admin_elu_add'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context['elu_form']
        self.assertTrue(form.errors['rank'])
        self.assertIn('Ce champ est obligatoire.', form.errors['rank'])

    def test_role_required(self):
        data = self.valid_president_data.copy()
        data['role'] = ''
        response = self.client.post(reverse('bureau-communautaire:admin_elu_add'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context['elu_form']
        self.assertTrue(form.errors['role'])
        self.assertIn('Ce champ est obligatoire.', form.errors['role'])

    def test_function_required(self):
        data = self.valid_president_data.copy()
        data['function'] = ''
        response = self.client.post(reverse('bureau-communautaire:admin_elu_add'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context['elu_form']
        self.assertTrue(form.errors['function'])
        self.assertIn('Ce champ est obligatoire.', form.errors['function'])

    def test_picture_required(self):
        data = self.valid_president_data.copy()
        data['picture'] = ''
        response = self.client.post(reverse('bureau-communautaire:admin_elu_add'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context['elu_form']
        self.assertTrue(form.errors['picture'])
        self.assertIn('Ce champ est obligatoire.', form.errors['picture'])

    def test_city_required(self):
        data = self.valid_president_data.copy()
        data['city'] = ''
        response = self.client.post(reverse('bureau-communautaire:admin_elu_add'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context['elu_form']
        self.assertTrue(form.errors['city'])
        self.assertIn('Ce champ est obligatoire.', form.errors['city'])

    def test_profession_required(self):
        data = self.valid_president_data.copy()
        data['profession'] = ''
        response = self.client.post(reverse('bureau-communautaire:admin_elu_add'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('bureau-communautaire:admin_elus_list'))
        self.assertTrue(Elus.objects.filter(first_name='Jean', last_name='Dupont').exists())

# ----------------------------------------------------------
# Test des vues pour les documents
# ----------------------------------------------------------
@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class DocumentTestCase(TestCase):
    """
    Teste le modèle Document.
    """
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
        self.client.login(email='admin@example.com', password='password123')  # Se connecter avec l'email

        # Créer un document de test
        self.document_content = b"This is a test document."
        self.document_file = SimpleUploadedFile("test.pdf", self.document_content, content_type="application/pdf")

        # Données de test pour le document
        self.document_data = {
            'title': 'Test Document',
            'document': self.document_file,
            'type': 'organigramme',
        }

    def tearDown(self):
        # Nettoyer les fichiers uploadés après chaque test
        Document.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    # Test de la vue d'ajout de document avec des données valides
    def test_views_add_document_valid_data(self):
        """
        Test de la vue d'ajout de document avec des données valides.
        """
        response = self.client.post(reverse('bureau-communautaire:admin_document_add'), self.document_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('bureau-communautaire:admin_documents_list'))
        self.assertTrue(Document.objects.filter(title='Test Document').exists())

    # Test de la vue d'ajout de document avec un titre invalide
    def test_views_add_document_invalid_title(self):
        """
        Test de la vue d'ajout de document avec un titre invalide.
        """
        data = self.document_data.copy()
        data['title'] = ''
        response = self.client.post(reverse('bureau-communautaire:admin_document_add'), data, follow=True)
        self.assertEqual(response.status_code, 200)
        form = response.context['document_form']
        self.assertTrue(form.errors['title'])
        self.assertIn('Ce champ est obligatoire.', form.errors['title'])

    # Test de la vue d'ajout de document avec un type invalide
    def test_views_add_document_invalid_type(self):
        """
        Test de la vue d'ajout de document avec un type invalide.
        """
        data = self.document_data.copy()
        data['type'] = ''
        response = self.client.post(reverse('bureau-communautaire:admin_document_add'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context['document_form']
        self.assertTrue(form.errors['type'])
        self.assertIn('Ce champ est obligatoire.', form.errors['type'])
    
    # Test de la vue d'ajout de document avec un fichier invalide
    def test_views_add_document_invalid_file(self):
        """
        Test de la vue d'ajout de document avec un fichier invalide.
        """
        data = self.document_data.copy()
        data['document'] = ''
        response = self.client.post(reverse('bureau-communautaire:admin_document_add'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context['document_form']
        self.assertTrue(form.errors['document'])
        self.assertIn('Ce champ est obligatoire.', form.errors['document'])