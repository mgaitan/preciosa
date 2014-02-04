from decimal import Decimal
import factory
from django.contrib.auth.models import User
from preciosa.precios.models import (Empresa, Marca, Cadena, Producto, Precio,
                                     PrecioEnAcuerdo, LocalComercial, Categoria)


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: 'user{0}'.format(n))
    password = 'pass'
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)


class CategoriaFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Categoria
    nombre = factory.Sequence(lambda n: 'Categoria_{0}'.format(n))
    depth = 1


class EmpresaFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Empresa
    nombre = factory.Sequence(lambda n: 'Empresa {0}'.format(n))


class CadenaFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Cadena
    nombre = factory.Sequence(lambda n: 'Cadena {0}'.format(n))


class LocalComercialFactory(factory.DjangoModelFactory):
    FACTORY_FOR = LocalComercial
    cadena = factory.SubFactory(CadenaFactory)


class MarcaFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Marca
    nombre = factory.Sequence(lambda n: 'Marca {0}'.format(n))
    empresa = factory.SubFactory(EmpresaFactory)


class ProductoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Producto
    categoria = factory.SubFactory(CategoriaFactory)
    descripcion = factory.Sequence(lambda n: 'Producto {0}'.format(n))
    marca = factory.SubFactory(MarcaFactory)


class PrecioFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Precio
    producto = factory.SubFactory(ProductoFactory)
    local = factory.SubFactory(LocalComercialFactory)
    precio = Decimal('1.0')


class PrecioEnAcuerdoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PrecioEnAcuerdo
    producto = factory.SubFactory(ProductoFactory)
    cadena = factory.SubFactory(CadenaFactory)
    precio_norte = Decimal('1.0')
    precio_sur = Decimal('1.1')
