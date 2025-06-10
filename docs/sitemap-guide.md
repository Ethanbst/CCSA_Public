# Guide d'utilisation et de maintenance du Sitemap

## Introduction

Ce document explique comment utiliser, maintenir et mettre à jour le sitemap XML du site web de la Communauté de Communes Sud-Avesnois (CCSA). Le sitemap est un fichier XML qui aide les moteurs de recherche à comprendre la structure de votre site et à indexer vos pages plus efficacement.

## Structure du sitemap

Le sitemap est généré automatiquement par Django à partir des URLs définies dans le fichier `home/sitemaps.py`. Il utilise le framework de sitemap intégré à Django.

### Fichiers concernés

- `home/sitemaps.py` : Définit les URLs à inclure dans le sitemap
- `app/urls.py` : Configure l'URL du sitemap (`/sitemap.xml`)
- `app/settings.py` : Inclut l'application `django.contrib.sitemaps`

## Accéder au sitemap

Le sitemap est accessible à l'URL suivante :

```
https://www.sud-avesnois.fr/sitemap.xml
```

En environnement de développement :

```
http://127.0.0.1:8000/sitemap.xml
```

## Mettre à jour le sitemap

### Ajouter de nouvelles pages

Pour ajouter de nouvelles pages au sitemap, vous devez mettre à jour la méthode `items()` dans la classe `StaticViewSitemap` du fichier `home/sitemaps.py` :

```python
def items(self):
    # Liste de tous les noms d'URL du site
    return [
        'home',
        'elus',
        # Ajoutez ici les nouveaux noms d'URL
        'nouvelle_page',
    ]
```

**Important** : Les noms d'URL doivent correspondre aux noms définis dans les fichiers `urls.py` (attribut `name` des routes).

### Modifier la priorité et la fréquence de mise à jour

Vous pouvez modifier la priorité et la fréquence de mise à jour des pages en modifiant les attributs `priority` et `changefreq` dans la classe `StaticViewSitemap` :

```python
class StaticViewSitemap(Sitemap):
    priority = 0.5  # Valeur entre 0.0 et 1.0
    changefreq = 'weekly'  # 'always', 'hourly', 'daily', 'weekly', 'monthly', 'yearly', 'never'
```

### Créer des sitemaps spécifiques

Si vous souhaitez définir des priorités ou fréquences différentes selon les pages, vous pouvez créer plusieurs classes de sitemap :

```python
class HighPrioritySitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['home', 'presentation']

class MediumPrioritySitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['elus', 'conseil', 'competences']
```

Puis mettre à jour le dictionnaire `sitemaps` dans `app/urls.py` :

```python
sitemaps = {
    'high_priority': HighPrioritySitemap,
    'medium_priority': MediumPrioritySitemap,
}
```

## Bonnes pratiques

1. **Maintenez le sitemap à jour** : Ajoutez les nouvelles pages dès qu'elles sont créées
2. **Respectez les fréquences de mise à jour** : Ne déclarez pas une page comme mise à jour quotidiennement si ce n'est pas le cas
3. **Utilisez les priorités avec parcimonie** : Réservez les priorités élevées (> 0.7) aux pages les plus importantes
4. **Vérifiez régulièrement la validité** : Utilisez des outils comme [Google Search Console](https://search.google.com/search-console) pour vérifier que votre sitemap est correctement indexé

## Soumettre le sitemap aux moteurs de recherche

### Google Search Console

1. Connectez-vous à [Google Search Console](https://search.google.com/search-console)
2. Sélectionnez votre propriété
3. Dans le menu de gauche, cliquez sur "Sitemaps"
4. Entrez l'URL de votre sitemap (par exemple, `https://www.sud-avesnois.fr/sitemap.xml`)
5. Cliquez sur "Soumettre"

### Bing Webmaster Tools

1. Connectez-vous à [Bing Webmaster Tools](https://www.bing.com/webmasters)
2. Sélectionnez votre site
3. Dans le menu "Configuration", cliquez sur "Sitemaps"
4. Entrez l'URL de votre sitemap
5. Cliquez sur "Soumettre"

## Dépannage

### Le sitemap n'est pas généré correctement

1. Vérifiez que `django.contrib.sitemaps` est bien dans `INSTALLED_APPS` dans `settings.py`
2. Vérifiez que les noms d'URL dans la méthode `items()` correspondent bien aux noms définis dans `urls.py`
3. Assurez-vous que toutes les URLs peuvent être résolues avec `reverse()`

### Erreurs 404 dans le sitemap

Si certaines URLs du sitemap renvoient des erreurs 404, vérifiez que :
1. Les vues correspondantes sont correctement implémentées
2. Les noms d'URL sont correctement définis
3. Les URLs sont accessibles manuellement

## Ressources

- [Documentation Django sur les sitemaps](https://docs.djangoproject.com/fr/5.1/ref/contrib/sitemaps/)
- [Protocol Sitemap](https://www.sitemaps.org/protocol.html)
- [Google Search Console](https://search.google.com/search-console)
- [Bing Webmaster Tools](https://www.bing.com/webmasters)
