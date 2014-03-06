# -*- coding: utf-8 -*-
from decimal import Decimal
import factory
from factory.fuzzy import FuzzyDecimal, BaseFuzzyAttribute
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from cities_light.models import City, Country
from preciosa.precios.models import (EmpresaFabricante, Marca, Cadena, Producto, Precio,
                                     PrecioEnAcuerdo, Sucursal, Categoria)


class FuzzyPoint(BaseFuzzyAttribute):

    def fuzz(self):
        # entre Rio Turbio y CABA
        longitude = FuzzyDecimal(-72.3367, -58.37723, precision=4)
        # entre Ushuaia y La Quiaca
        latitude = FuzzyDecimal(-54.8, -22.1023, precision=4)
        return Point(float(longitude.fuzz()),
                     float(latitude.fuzz()), srid=4326)


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: u'user{0}'.format(n))
    password = 'pass'
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)


class CategoriaFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Categoria
    nombre = factory.Sequence(lambda n: u'Categoria_{0}'.format(n))
    depth = 1
    path = factory.Sequence(lambda n: u'000{0}'.format(chr(n + 65)))


class EmpresaFabricanteFactory(factory.DjangoModelFactory):
    FACTORY_FOR = EmpresaFabricante
    nombre = factory.Sequence(lambda n: u'Empresa {0}'.format(n))


class CadenaFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Cadena
    nombre = factory.Sequence(lambda n: u'Cadena {0}'.format(n))


class CountryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Country
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)
    name = factory.Sequence(lambda n: u'Country {0}'.format(n))


class CityFactory(factory.DjangoModelFactory):
    FACTORY_FOR = City
    name = factory.Sequence(lambda n: u'Ciudad {0}'.format(n))
    # entre Rio Turbio y CABA
    longitude = FuzzyDecimal(-72.3367, -58.37723, precision=4)
    # entre Ushuaia y La Quiaca
    latitude = FuzzyDecimal(-54.8, -22.1023, precision=4)
    country = CountryFactory(name='Argentina')


class SucursalFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Sucursal
    cadena = factory.SubFactory(CadenaFactory)
    ciudad = factory.SubFactory(CityFactory)
    direccion = factory.Sequence(lambda n: u'San Martín {0}00'.format(n))
    ubicacion = FuzzyPoint()


class MarcaFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Marca
    nombre = factory.Sequence(lambda n: u'Marca {0}'.format(n))
    fabricante = factory.SubFactory(EmpresaFabricanteFactory)


class ProductoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Producto
    categoria = factory.SubFactory(CategoriaFactory, depth=3)
    descripcion = factory.Sequence(lambda n: u'Producto {0}'.format(n))
    marca = factory.SubFactory(MarcaFactory)
    unidad_medida = Producto.UM_L
    contenido = 10


class PrecioFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Precio
    producto = factory.SubFactory(ProductoFactory)
    sucursal = factory.SubFactory(SucursalFactory)
    precio = Decimal('1.0')


class PrecioEnAcuerdoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PrecioEnAcuerdo
    producto = factory.SubFactory(ProductoFactory)
    cadena = factory.SubFactory(CadenaFactory)
    precio_norte = Decimal('1.0')
    precio_sur = Decimal('1.1')
