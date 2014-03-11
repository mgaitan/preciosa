from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from precios import views

from accounts.views import SignupView

from django.views.generic.base import RedirectView

import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns("",
    url(r'^api/v1/', include("preciosa.api.urls")),  # noqa
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/signup/$", SignupView.as_view()),
    url(r"^account/", include("account.urls")),
    url(r'^newsletter/', include('newsletter.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^imperavi/', include('imperavi.urls')),
    url(r'^autocomplete/buscador/', views.autocomplete_buscador, name='autocomplete_buscador'),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^(\d+)-([a-z0-9-_]+)/$',
        views.ProductosListView.as_view(), name='lista_productos'),
    url(r'^(\d+)-([a-z0-9-_]+)/(?P<pk>\d+)-([a-z0-9-_]+)$',
        views.ProductoDetailView.as_view(),
        name='detalle_producto'),
    url(r'^home/$', RedirectView.as_view(url='/'), name='home'),


    url(r'^blog/', include('radpress.urls')),
    url(r"^voluntarios/", include("preciosa.voluntarios.urls")),

)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
