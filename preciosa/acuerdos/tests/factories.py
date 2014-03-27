import factory
from preciosa.precios.tests.factories import RegionFactory as ProvinciaFactory
from preciosa.acuerdos.models import Region


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
