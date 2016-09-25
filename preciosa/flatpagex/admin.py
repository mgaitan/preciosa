from django.contrib import admin

from django.contrib.flatpages.models import FlatPage
from preciosa.flatpagex.models import FlatPageX
from django_summernote.admin import SummernoteModelAdmin


class CustomFlatPageAdmin(SummernoteModelAdmin):
    pass


admin.site.unregister(FlatPage)
admin.site.register(FlatPageX, CustomFlatPageAdmin)

