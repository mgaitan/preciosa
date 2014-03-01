from django.conf.urls import patterns, url


urlpatterns = patterns("preciosa.voluntarios.views",
    url(r"^$", 'dashboard', name='voluntarios_dashboard'),      # noqa
    url(r"^mapa_categorias/$", 'mapa_categorias', name='mapa_categorias'),
    url(r"^logos/$", 'logos', name='logos'),
    url(r"^logos/marca/(?P<pk>\d+)/paso-(?P<paso>1|2)/$", 'logos', name='logos_marca'),
    url(r"^marca/$", 'alta_marca', name='alta_marca'),
    url(r"^marca/autocomplete/nombre/$", 'autocomplete_nombre_marca',
        name='autocomplete_nombre_marca'),
    url(r"^marca/voto/(?P<pk>\d+)/$", 'voto_item', name='voto_item'),
    url(r"^sucursal/$", 'alta_cadena_sucursal', name='alta_cadena_sucursal'),
    url(r"^sucursal/autocomplete/nombre/$", 'autocomplete_nombre_sucursal',
        name='autocomplete_nombre_sucursal'),
    url(r"^sucursal/voto/(?P<pk>\d+)/$", 'voto_item', name='voto_item'),
    url(r"^sucursal/geo_code/$", 'geo_code_data', name='geo_code_data')
)
