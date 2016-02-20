from dal import autocomplete
from django.db.models import Q
from cities_light.models import City


class CityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.q or len(self.q) < 4:
            return City.objects.none()
        return City.objects.filter(Q(name__icontains=self.q) |
                                   Q(alternate_names__icontains=self.q))

