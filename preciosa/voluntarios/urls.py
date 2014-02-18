from django.conf.urls import patterns, include, url


urlpatterns = patterns("preciosa.voluntarios.views",
    url(r"^$", 'dashboard', name='voluntarios_dashboard'),
    url(r"^mapa_categorias/$", 'mapa_categorias', name='mapa_categorias'),
    url(r"^logos/(?P<pk>\d+)?/$", 'logos', name='logos'),
)