from django.contrib import admin
from preciosa.acuerdos.models import Acuerdo, PrecioEnAcuerdo, Region

admin.site.register(Acuerdo)
admin.site.register(Region)
admin.site.register(PrecioEnAcuerdo)
