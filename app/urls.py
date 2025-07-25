from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.sitemaps.views import sitemap
from home.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
     path('ccsa-admin/', admin.site.urls),
     path('', include('home.urls')),
     path('', include('accounts.urls', namespace='accounts')),
     path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
          name='django.contrib.sitemaps.views.sitemap'),
     path('', include('conseil_communautaire.urls')),
     path('', include('journal.urls', namespace='journal')),
     path('', include('bureau_communautaire.urls', namespace='bureau-communautaire')),
     path('', include('communes_membres.urls', namespace='communes-membres')),
     path('', include('commissions.urls', namespace='commissions')),
     path('', include('competences.urls', namespace='competences')),
     path('', include('semestriels.urls', namespace='semestriels')),
     path('', include('comptes_rendus.urls', namespace='comptes_rendus')),
     path('services/', include('services.urls', namespace='services')),
     path('', include('rapports_activite.urls',
                      namespace='rapports_activite')),
     path('', include('contact.urls', namespace='contact')),
     # Redirections pour les URLs courtes
     path('login/', RedirectView.as_view(pattern_name='accounts:login'),
          name='login_redirect'),
     path('logout/', RedirectView.as_view(pattern_name='accounts:logout'),
          name='logout_redirect'),
     path('register/', RedirectView.as_view(pattern_name='accounts:register'),
          name='register_redirect'),
     path('profile/', RedirectView.as_view(pattern_name='accounts:profile'),
          name='profile_redirect'),
]
