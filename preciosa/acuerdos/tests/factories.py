# -*- coding: utf-8 -*-
import factory
from decimal import Decimal
from preciosa.precios.tests.factories import (RegionFactory as ProvinciaFactory,
                                              ProductoFactory)
from preciosa.acuerdos.models import Region, Acuerdo, PrecioEnAcuerdo


class RegionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Region
    nombre = factory.Sequence(lambda n: u'Region de Acuerdo {0}'.format(n))

    @factory.post_generation
    def provincias(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of provincias were passed in, use them
            for prov in extracted:
                self.provincias.add(prov)
        else:
            # default, una provincia
            self.provincias.add(ProvinciaFactory())

    @factory.post_generation
    def ciudades_incluidas(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for ciudad in extracted:
                self.ciudades_incluidas.add(ciudad)

    @factory.post_generation
    def ciudades_excluidas(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for ciudad in extracted:
                self.ciudades_excluidas.add(ciudad)


class AcuerdoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Acuerdo
    FACTORY_DJANGO_GET_OR_CREATE = ('nombre',)
    nombre = factory.Sequence(lambda n: u'Acuerdo de precios {0}'.format(n))
    region = factory.SubFactory(RegionFactory)

    @factory.post_generation
    def cadenas(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for cadena in extracted:
                self.cadenas.add(cadena)

    @factory.post_generation
    def sucursales(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for suc in extracted:
                self.sucursales.add(suc)


class PrecioEnAcuerdoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PrecioEnAcuerdo
    acuerdo = factory.SubFactory(AcuerdoFactory)
    producto = factory.SubFactory(ProductoFactory)
    precio = Decimal('10.0')

