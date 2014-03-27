from django.test import TestCase
from preciosa.precios.tests.factories import (RegionFactory as ProvinciaFactory,
                                              CityFactory)
from preciosa.acuerdos.tests.factories import RegionFactory


class TestRegion(TestCase):

    def setUp(self):
        # creo algunas ciudades pertenencientes a una una region/provincia
        self.prov = ProvinciaFactory()
        self.ciudades_en_prov = [CityFactory(region=self.prov),
                                 CityFactory(region=self.prov)]

    def test_ciudades_en_acuerdo_por_provincia(self):
        # creo una region
        region = RegionFactory(provincias=[self.prov])
        for c in self.ciudades_en_prov:
            self.assertIn(c, region.ciudades())

    def test_contempla_ciudades_incluidas(self):
        otra_ciudad1 = CityFactory()
        otra_ciudad2 = CityFactory()
        ciudades = self.ciudades_en_prov + [otra_ciudad1, otra_ciudad2]
        region = RegionFactory(provincias=[self.prov],
                               ciudades_incluidas=[otra_ciudad1, otra_ciudad2])
        for c in ciudades:
            self.assertIn(c, region.ciudades())

    def test_excluye_ciudades_incluidas(self):
        region = RegionFactory(provincias=[self.prov],
                               ciudades_excluidas=self.ciudades_en_prov[1:])
        self.assertIn(self.ciudades_en_prov[0], region.ciudades())
        self.assertNotIn(self.ciudades_en_prov[1], region.ciudades())
