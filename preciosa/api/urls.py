from django.conf.urls import patterns, url

urlpatterns = patterns("preciosa.api.views",
    url(r"^sucursales/$", 'sucursales_list', name='api_sucursales'),
)
