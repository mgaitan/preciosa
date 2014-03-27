# -*- coding: utf-8 -*-
"""
esta app modela el programa Precios Cuidados
ver https://github.com/mgaitan/preciosa/issues/137
"""

from django.db import models
from django.db.models import Q
from cities_light.models import City


class Region(models.Model):
    """una region incluye provincias y opcionalmente agrega o quita
    algunas ciudades. especificas"""

    nombre = models.CharField(max_length=150)
    provincias = models.ManyToManyField('cities_light.Region')
    ciudades_incluidas = models.ManyToManyField('cities_light.City',
                                                related_name='incluida_en_region_acuerdo')
    ciudades_excluidas = models.ManyToManyField('cities_light.City',
                                                related_name='excluida_de_region_acuerdo')

    def ciudades(self):
        """devuelve un QS de ciudades incluyendo todas las ciudades
           que abarca la region. considera provincia, ciudades incluidas y
           excluidas"""
        base = City.objects.filter(Q(incluida_en_region_acuerdo=self) |
                                   Q(region__in=self.provincias.all()))
        return base.exclude(Q(excluida_de_region_acuerdo=self))
