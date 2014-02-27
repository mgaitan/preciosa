from decimal import Decimal
import factory
from django.contrib.auth.models import User
from cities_light.models import City, Country
from preciosa.precios.models import (EmpresaFabricante, Marca, Cadena, Producto, Precio,
                                     PrecioEnAcuerdo, Sucursal, Categoria)


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    password = 'pass'
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)


class CategoriaFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Categoria
    nombre = factory.Sequence(lambda n: 'Categoria_{0}'.format(n))
    depth = 1


class EmpresaFabricanteFactory(factory.DjangoModelFactory):
    FACTORY_FOR = EmpresaFabricante
    nombre = factory.Sequence(lambda n: 'Empresa {0}'.format(n))


class CadenaFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Cadena
    nombre = factory.Sequence(lambda n: 'Cadena {0}'.format(n))


class CountryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Country
    FACTORY_DJANGO_GET_OR_CREATE = ('name',)
    name = factory.Sequence(lambda n: 'Country {0}'.format(n))


class CityFactory(factory.DjangoModelFactory):
    FACTORY_FOR = City
    name = factory.Sequence(lambda n: 'Ciudad {0}'.format(n))
    country = CountryFactory(name='Argentina')


class SucursalFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Sucursal
    cadena = factory.SubFactory(CadenaFactory)
    ciudad = factory.SubFactory(CityFactory)


class MarcaFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Marca
    nombre = factory.Sequence(lambda n: 'Marca {0}'.format(n))
    fabricante = factory.SubFactory(EmpresaFabricanteFactory)


class ProductoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Producto
    categoria = factory.SubFactory(CategoriaFactory)
    descripcion = factory.Sequence(lambda n: 'Producto {0}'.format(n))
    marca = factory.SubFactory(MarcaFactory)


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
