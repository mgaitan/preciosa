from django.contrib import admin

from django.contrib.flatpages.models import FlatPage
from preciosa.flatpagex.models import FlatPageX
from imperavi.admin import ImperaviAdmin


class CustomFlatPageAdmin(ImperaviAdmin):
    pass


admin.site.unregister(FlatPage)
admin.site.register(FlatPageX, CustomFlatPageAdmin)

