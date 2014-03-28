# -*- coding: utf-8 -*-
"""
esta app modela el programa Precios Cuidados
ver https://github.com/mgaitan/preciosa/issues/137
"""

from django.db import models
from django.db.models.signals import m2m_changed
from django.db.models import Q
from cities_light.models import City


class Region(models.Model):
    """una region incluye provincias y opcionalmente agrega o quita
    algunas ciudades. especificas"""

    nombre = models.CharField(max_length=150)
    provincias = models.ManyToManyField('cities_light.Region',
                                        related_name='incluida_en_region_acuerdo')
    ciudades_incluidas = models.ManyToManyField('cities_light.City',
                                                related_name='incluida_en_region_acuerdo')
    ciudades_excluidas = models.ManyToManyField('cities_light.City',
                                                related_name='excluida_de_region_acuerdo')

    # este campo es una denormalización para simplificar y agilizar queries
    # se actualiza llamando a _calcular_ciudades cuando algunos los otros m2m
    # cambia.
    ciudades = models.ManyToManyField('cities_light.City',
                                      related_name='region_en_acuerdo',
                                      editable=False)

    def __unicode__(self):
        return self.nombre

    def _calcular_ciudades(self):
        """devuelve un QS de ciudades incluyendo todas las ciudades
           que abarca la region. considera provincia, ciudades incluidas y
           excluidas"""
        base = City.objects.filter(Q(incluida_en_region_acuerdo=self) |
                                   Q(region__in=self.provincias.all()))
        return base.exclude(Q(excluida_de_region_acuerdo=self))


def actualizar_ciudades_de_region(sender, **kwargs):
    region = kwargs['instance']
    region.ciudades.clear()
    region.ciudades.add(*region._calcular_ciudades())

m2m_changed.connect(actualizar_ciudades_de_region,
                    sender=Region.ciudades_incluidas.through)
m2m_changed.connect(actualizar_ciudades_de_region,
                    sender=Region.ciudades_excluidas.through)
m2m_changed.connect(actualizar_ciudades_de_region,
                    sender=Region.provincias.through)


class Acuerdo(models.Model):
    nombre = models.CharField(max_length=150)
    region = models.ForeignKey(Region)
    sucursales = models.ManyToManyField('precios.Sucursal')
    cadenas = models.ManyToManyField('precios.Cadena')

    def __unicode__(self):
        tipo = 'Cadenas Nacionales' if self.cadenas.exists() else 'Super Regionales'
        return u"%s (%s) - %s" % (self.nombre, self.region, tipo)


class PrecioEnAcuerdoManager(models.Manager):

    def en_acuerdo(self, producto, sucursal):
        """dado un producto y sucursal, devuelve una lista de diccionarios
            con el precio y el nombre del acuerdo"""

        qs = super(PrecioEnAcuerdoManager, self).get_queryset()
        qs = qs.filter(producto=producto)

        # para evitar calcular todo. Si bien hacemos una query mas,
        # el porcentaje de productos bajo acuerdo es muy pequeño
        # la mayoria de las veces no existe.
        if not qs.exists():
            return []

        if sucursal.cadena:
            # grandes cadenas.
            qs = qs.filter(Q(acuerdo__cadenas=sucursal.cadena) |
                           Q(acuerdo__sucursales=sucursal))
        else:
            qs = qs.filter(acuerdo__sucursales=sucursal)

        qs = qs.filter(acuerdo__region__ciudades=sucursal.ciudad)
        return qs.values('acuerdo__nombre', 'precio')


class PrecioEnAcuerdo(models.Model):
    objects = PrecioEnAcuerdoManager()

    acuerdo = models.ForeignKey(Acuerdo, related_name='precios_en_acuerdo')
    producto = models.ForeignKey('precios.Producto')
    precio = models.DecimalField(max_digits=8, decimal_places=2)
