from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework import routers
from precios import views

router = routers.DefaultRouter()
router.register(r'cadenas', views.CadenaViewSet)
router.register(r'sucursales', views.SucursalViewSet)
router.register(r'ciudades', views.CityViewSet)


from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns("",
    url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),

    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("account.urls")),
    url(r'^(\d+)-([a-z0-9-]+)/$',
        views.ProductosListView.as_view(), name='lista_productos'),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
