import autocomplete_light
from cities_light.models import City


class CityAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name', 'alternate_names']


autocomplete_light.register(City, CityAutocomplete)
