from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from precios import views

from django.views.generic.base import RedirectView

import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns("",
    url(r'^api/v1/', include("preciosa.api.urls")),  # noqa
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("account.urls")),
    url(r'^newsletter/', include('newsletter.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^imperavi/', include('imperavi.urls')),
    url(r'^(\d+)-([a-z0-9-]+)/$',
        views.ProductosListView.as_view(), name='lista_productos'),
    url(r'^(\d+)-([a-z0-9-]+)/(?P<pk>\d+)-([a-z0-9-]+)$',
        views.ProductoDetailView.as_view(),
        name='detalle_producto'),
    url(r'^home/$', RedirectView.as_view(url='/'), name='home'),
    url(r'^autocomplete/', views.autocomplete, name='autocomplete'),

    url(r'^blog/', include('radpress.urls')),
    url(r"^voluntarios/", include("preciosa.voluntarios.urls")),

)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
