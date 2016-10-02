from django.conf import settings
from django.conf.urls import include, url
from precios import views


from accounts.views import SignupView

from django.views.generic.base import RedirectView


from django.contrib import admin
admin.autodiscover()


urlpatterns = [
    url(r'^api/v1/', include("preciosa.api.urls")),  # noqa
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/signup/$", SignupView.as_view(
        template_name_email_confirmation_sent='account/email/template_name_email_confirmation_sent')),
    url(r"^account/", include("account.urls")),
    # url(r'^newsletter/', include('newsletter.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^buscador/', views.ProductosSearchAutocomplete.as_view(), name='buscador'),
    url(r'^(\d+)-([a-z0-9-_]+)/$',
        views.ProductosListView.as_view(), name='lista_productos'),
    url(r'^(\d+)-([a-z0-9-_]+)/(?P<pk>\d+)-([a-z0-9-_]+)$',
        views.ProductoDetailView.as_view(),
        name='detalle_producto'),
    url(r'^home/$', RedirectView.as_view(url='/'), name='home'),


    url(r'^blog/', include('radpress.urls')),
    url(r"^voluntarios/", include("preciosa.voluntarios.urls")),
]


if settings.SITE_ID == 3:
    # las crawlers no son bienvenidos en el sitio de desarrollo
    from django.http import HttpResponse
    urlpatterns += [
        url(r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain"))
    ]
                            
