from django.conf.urls import patterns, url, include
from rest_framework import routers
from preciosa.api import views


router = routers.DefaultRouter()
router.register(r'cadenas', views.CadenaViewSet)
router.register(r'sucursales', views.SucursalViewSet)
router.register(r'ciudades', views.CityViewSet)


urlpatterns = patterns("preciosa.api.views",
    url(r"^sucursales/$", 'sucursales_list', name='api_sucursales'),
    url(r"^", include(router.urls))
)
