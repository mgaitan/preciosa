# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from rest_framework import routers
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from preciosa.api import views


class MyRouter(routers.DefaultRouter):

    def get_api_root_view(self):
        """
        Es la misma implementacion de la api root view de del
        DefaultRouter, pero con urls nuestras registradas.

        No es muy elegante, pero no encontré otra forma de
        registrar urls propias y las automaticas generadas por el router
        """
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        class APIRoot(APIView):
            _ignore_model_permissions = True

            def get(self, request, format=None):
                ret = {
                    'sucursales': reverse('sucursales', request=request),
                    'productos': reverse('productos', request=request),
                    'precios': reverse('precios', request=request),
                    'donde_queda': reverse('donde_queda', request=request),
                    # listar acá otras urls que queremos que aparezcan en
                    # la home de la API
                }
                for key, url_name in api_root_dict.items():
                    ret[key] = reverse(url_name, request=request, format=format)
                return Response(ret)

        return APIRoot.as_view()


router = MyRouter()
router.register(r'cadenas', views.CadenaViewSet)
router.register(r'ciudades', views.CityViewSet)
router.register(r'marcas', views.MarcaViewSet)
router.register(r'fabricantes', views.EmpresaFabricanteViewSet)
router.register(r'categorias', views.CategoriaViewSet)


urlpatterns = patterns("preciosa.api.views",
    url(r"^sucursales/$", views.SucursalesList.as_view(), name='sucursales'),
    url(r"^sucursales/(?P<pk>\d+)$", views.SucursalesList.as_view(),
        name='sucursal_detalle'),
    url(r"^sucursales/(?P<pk>\d+)/productos$",
        views.ProductosList.as_view(),
        name='productos_con_precio_en_sucursal'),
    url(r"^sucursales/(?P<pk_sucursal>\d+)/productos/(?P<pk_producto>\d+)$",
        views.producto_sucursal_detalle,
        name='producto_detalle'),
    url(r"^productos_mejores/(?P<pk_producto>\d+)$",
        views.producto_detalle,
        name='producto_detalle_coor'),
    url(r"^productos/$", views.ProductosList.as_view(), name='productos'),

    url(r"^productos/(?P<pk>\d+)$", views.ProductosList.as_view(), name='productos'),
    url(r"^precios/$", views.PreciosList.as_view(), name='precios'),
    url(r"^utils/donde_queda$", views.donde_queda, name='donde_queda'),

    url(r"^", include(router.urls))

)

urlpatterns += patterns('',
    url(r'^auth/token$', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^auth/registro$', views.registro, name='registro')
)

