from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """
    Sitemap pour les vues statiques du site.
    """
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        # Liste de tous les noms d'URL du site
        return [
            'home',
            'elus',
            'conseil',
            'commune',
            'comptes_rendus',
            'presentation',
            'competences',
            'journal',
            'commissions',
            'marches_publics',
            'mobilite',
            'habitat',
            'collecte_dechets',
            'encombrants',
            'dechetteries',
            'maisons_sante',
            'mutuelle',
            'plui',
            'projet_plui',
            'equipe',
            'semestriel',
            'rapports_activite',
            'mentions_legales',
            'politique_confidentialite',
        ]

    def location(self, item):
        return reverse(item)
