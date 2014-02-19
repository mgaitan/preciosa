from django.conf.urls import patterns, include, url


urlpatterns = patterns("preciosa.voluntarios.views",
    url(r"^$", 'dashboard', name='voluntarios_dashboard'),
    url(r"^mapa_categorias/$", 'mapa_categorias', name='mapa_categorias'),
    url(r"^logos/$", 'logos', name='logos'),
    url(r"^logos/marca/(?P<pk>\d+)/paso-(?P<paso>1|2)/$", 'logos', name='logos_marca'),
    url(r"^marca/", 'alta_marca', name='alta_marca'),
    url(r"^marca/(?P<pk>\d+)/", 'alta_marca', name='alta_marca_2'),
)