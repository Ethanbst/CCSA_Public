from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from competences.models import Competence

User = get_user_model()

MEDIA_ROOT = 'test_competences_media'  # Répertoire temporaire pour les fichiers médias

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CompetenceViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer un superutilisateur personnalisé
        cls.superuser = User.objects.create_superuser(
            email='admin@example.com',  # Utiliser l'email comme nom d'utilisateur
            password='password123'
        )

    def setUp(self):
            # print("Connexion avec le compte super_user\n")
            self.client = Client()
            self.client.login(email='admin@example.com', password='password123')  # Se connecter avec l'email

    # Test de la vue de la liste public des compétences
    def test_competence_list_view_without_data(self):
        """
        Test de la vue de la liste public des compétences
        """
        response = self.client.get(reverse('competences:competences'))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'competences/competences.html')

        # Vérifier qu'aucune compétence n'est affichée
        self.assertContains(response, "Aucune compétence facultative n'est disponible.")
        self.assertContains(response, "Aucune compétence obligatoire n'est disponible.")
        self.assertContains(response, "Aucune compétence optionnelle n'est disponible.")

    # Test de la vue de la liste admin des compétences
    def test_competence_list_view_admin_without_data(self):
        """
        Test de la vue de la liste admin des compétences
        """
        # print("Test de la vue de la liste admin des compétences\n")
        response = self.client.get(reverse('competences:admin_competences_list'))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'competences/admin_competences_list.html')

        # Vérifier qu'aucune compétence n'est affichée
        self.assertContains(response, "Aucune compétence trouvée.")
    
    # Test de la vue de la liste public des compétences avec des données
    def test_competence_list_view_with_data(self):
        """
        Test de la vue de la liste public des compétences avec des données
        """
        # Créer une compétence pour le test
        competence_ob = Competence.objects.create(
            title='Test Compétence Obligatoire',
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description='Ceci est une compétence obligatoire de test.',
            category=Competence.Category.OBLIGATOIRE,
            is_big=False
        )

        competence_f = Competence.objects.create(
            title='Test Compétence Facultative',
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description='Ceci est une compétence facultative de test.',
            category=Competence.Category.FACULTATIVE,
            is_big=False
        )

        competence_op = Competence.objects.create(
            title='Test Compétence Optionnelle',
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description='Ceci est une compétence optionnelle de test.',
            category=Competence.Category.OPTIONNELLE,
            is_big=False
        )

        response = self.client.get(reverse('competences:competences'))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'competences/competences.html')

        # Vérifier que les compétences sont affichées
        self.assertContains(response, competence_ob.title)
        self.assertContains(response, competence_f.title)
        self.assertContains(response, competence_op.title)
        self.assertContains(response, competence_ob.description)
        self.assertContains(response, competence_f.description)
        self.assertContains(response, competence_op.description)
        self.assertContains(response, competence_ob.icon)
        self.assertContains(response, competence_f.icon)
        self.assertContains(response, competence_op.icon)

    # Test de la vue de la liste admin des compétences avec des données
    def test_competence_list_view_admin_with_data(self):
        """
        Test de la vue de la liste admin des compétences avec des données
        """
        # Créer une compétence pour le test
        competence_ob = Competence.objects.create(
            title='Test Compétence Obligatoire',
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description='Ceci est une compétence obligatoire de test.',
            category=Competence.Category.OBLIGATOIRE,
            is_big=False
        )

        competence_f = Competence.objects.create(
            title='Test Compétence Facultative',
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description='Ceci est une compétence facultative de test.',
            category=Competence.Category.FACULTATIVE,
            is_big=False
        )

        competence_op = Competence.objects.create(
            title='Test Compétence Optionnelle',
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description='Ceci est une compétence optionnelle de test.',
            category=Competence.Category.OPTIONNELLE,
            is_big=False
        )

        response = self.client.get(reverse('competences:admin_competences_list'))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'competences/admin_competences_list.html')

        # Vérifier que les compétences sont affichées
        self.assertContains(response, competence_ob.title)
        self.assertContains(response, competence_f.title)
        self.assertContains(response, competence_op.title)
        self.assertContains(response, competence_ob.description)
        self.assertContains(response, competence_f.description)
        self.assertContains(response, competence_op.description)
        self.assertContains(response, competence_ob.icon)
        self.assertContains(response, competence_f.icon)
        self.assertContains(response, competence_op.icon)

    # Test de la vue d'ajout de compétence
    def test_add_competence_view(self):
        """
        Test de la vue d'ajout de compétence
        """
        response = self.client.get(reverse('competences:add_competence'))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'competences/admin_competence_add.html')
        # Vérifier que le bouton "Publier" est présent
        self.assertContains(response, "Publier")

    def test_add_competence_view_post_valid_data(self):
        """
        Test de la vue d'ajout de compétence avec des données valides
        """
        response = self.client.post(reverse('competences:add_competence'), {
            'title': 'Test Compétence',
            'icon': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            'description': 'Ceci est une compétence de test.',
            'category': Competence.Category.OBLIGATOIRE,
            'is_big': False
        })
        # Vérifier que la réponse est une redirection
        self.assertEqual(response.status_code, 302)
        # Vérifier que la compétence a été créée
        competence = Competence.objects.get(title='Test Compétence')
        self.assertEqual(competence.title, 'Test Compétence')
        self.assertEqual(competence.icon, '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>')
        self.assertEqual(competence.description, 'Ceci est une compétence de test.')
        self.assertEqual(competence.category, Competence.Category.OBLIGATOIRE)
        self.assertEqual(competence.is_big, False)

    def test_add_competence_view_post_invalid_data(self):
        """
        Test de la vue d'ajout de compétence avec des données invalides
        """
        response = self.client.post(reverse('competences:add_competence'), {
            'title': '',
            'icon': '',
            'description': '',
            'category': '',
            'is_big': False
        })
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'competences/admin_competence_add.html')
        self.assertEqual(Competence.objects.count(), 0)  # Vérifier qu'aucune compétence n'a été créée

    # Test de la vue de modification de compétence
    def test_edit_competence_view(self):
        """
        Test de la vue de modification de compétence
        """
        # Créer une compétence pour le test
        competence = Competence.objects.create(
            title='Test Compétence',
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description='Ceci est une compétence de test.',
            category=Competence.Category.OBLIGATOIRE,
            is_big=False
        )

        response = self.client.get(reverse('competences:edit_competence', args=[competence.id]))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'competences/admin_competence_edit.html')
        # Vérifier que le bouton est présent
        self.assertContains(response, "Appliquer")
        # Vérifier que le formulaire contient les données de la compétence
        self.assertContains(response, competence.title)
        self.assertContains(response, competence.description)

    def test_edit_competence_view_post_valid_data(self):
        """
        Test de la vue de modification de compétence avec des données valides
        """
        # Créer une compétence pour le test
        competence = Competence.objects.create(
            title='Test Compétence',
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description='Ceci est une compétence de test.',
            category=Competence.Category.OBLIGATOIRE,
            is_big=False
        )

        response = self.client.post(reverse('competences:edit_competence', args=[competence.id]), {
            'title': 'Test Compétence Modifiée',
            'icon': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            'description': 'Ceci est une compétence modifiée de test.',
            'category': Competence.Category.FACULTATIVE,
            'is_big': True
        })
        # Vérifier que la réponse est une redirection
        self.assertEqual(response.status_code, 302)
        # Vérifier que la compétence a été modifiée
        competence.refresh_from_db()
        self.assertEqual(competence.title, 'Test Compétence Modifiée')
        self.assertEqual(competence.icon, '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>')
        self.assertEqual(competence.description, 'Ceci est une compétence modifiée de test.')
        self.assertEqual(competence.category, Competence.Category.FACULTATIVE)
        self.assertEqual(competence.is_big, True)

    def test_edit_competence_view_post_invalid_data(self):
        """
        Test de la vue de modification de compétence avec des données invalides
        """
        # Créer une compétence pour le test
        competence = Competence.objects.create(
            title='Test Compétence',
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description='Ceci est une compétence de test.',
            category=Competence.Category.OBLIGATOIRE,
            is_big=False
        )

        response = self.client.post(reverse('competences:edit_competence', args=[competence.id]), {
            'title': '',
            'icon': '',
            'description': '',
            'category': '',
            'is_big': False
        })
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'competences/admin_competence_edit.html')
        self.assertEqual(competence.title, 'Test Compétence')
        self.assertEqual(competence.icon, '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>')
        self.assertEqual(competence.description, 'Ceci est une compétence de test.')
        self.assertEqual(competence.category, Competence.Category.OBLIGATOIRE)

    # Test de la vue de suppression de compétence
    def test_delete_competence_view(self):
        """
        Test de la vue de suppression de compétence
        """
        # Créer une compétence pour le test
        competence = Competence.objects.create(
            title='Test Compétence',
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description='Ceci est une compétence de test.',
            category=Competence.Category.OBLIGATOIRE,
            is_big=False
        )

        response = self.client.get(reverse('competences:delete_competence', args=[competence.id]))
        # Vérifier que la réponse est 200 OK
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'competences/admin_competence_delete.html')
        # Vérifier que le bouton est présent
        self.assertContains(response, "Supprimer")

    def test_delete_competence_view_post(self):
        """
        Test de la vue de suppression de compétence
        """
        # Créer une compétence pour le test
        competence = Competence.objects.create(
            title='Test Compétence',
            icon='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2L2 7h20L12 2zM2 17l10 5 10-5V7H2v10z"/></svg>',
            description='Ceci est une compétence de test.',
            category=Competence.Category.OBLIGATOIRE,
            is_big=False
        )

        response = self.client.post(reverse('competences:delete_competence', args=[competence.id]))
        # Vérifier que la réponse est une redirection
        self.assertEqual(response.status_code, 302)
        # Vérifier que la compétence a été supprimée
        self.assertFalse(Competence.objects.filter(id=competence.id).exists())