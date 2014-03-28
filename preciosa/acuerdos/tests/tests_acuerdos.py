from decimal import Decimal
from django.test import TestCase
from preciosa.precios.tests.factories import (RegionFactory as ProvinciaFactory,
                                              CityFactory, SucursalFactory,
                                              CadenaFactory, ProductoFactory)
from preciosa.acuerdos.tests.factories import (RegionFactory,
                                               PrecioEnAcuerdoFactory,
                                               AcuerdoFactory)
from preciosa.acuerdos.models import PrecioEnAcuerdo


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
            self.assertIn(c, region.ciudades.all())

    def test_incluye_ciudades_especificas(self):
        otra_ciudad1 = CityFactory()
        otra_ciudad2 = CityFactory()
        ciudades = self.ciudades_en_prov + [otra_ciudad1, otra_ciudad2]
        region = RegionFactory(provincias=[self.prov],
                               ciudades_incluidas=[otra_ciudad1, otra_ciudad2])
        for c in ciudades:
            self.assertIn(c, region.ciudades.all())

    def test_excluye_ciudades_especificas(self):
        region = RegionFactory(provincias=[self.prov],
                               ciudades_excluidas=self.ciudades_en_prov[1:])
        self.assertIn(self.ciudades_en_prov[0], region.ciudades.all())
        self.assertNotIn(self.ciudades_en_prov[1], region.ciudades.all())


class TestPrecioEnAcuerdo(TestCase):

    def setUp(self):
        self.producto = ProductoFactory()
        self.carrefour = CadenaFactory(nombre='Carrefour')
        self.sucursales_carrefour = suc1, suc2 = [SucursalFactory(cadena=self.carrefour),
                                                  SucursalFactory(cadena=self.carrefour)]
        self.super_regional = SucursalFactory(nombre='Lo de Cacho')

        # lo de cacho queda en y una de carrefour queda en NOA
        self.noa = RegionFactory(nombre="NOA",
                                 ciudades_incluidas=[suc2.ciudad,
                                                     self.super_regional.ciudad])
        # una de carrefour en Caba
        self.caba = RegionFactory(nombre="CABA",
                                  ciudades_incluidas=[suc1.ciudad])

    def acuerdo(self, sucursal):
        return list(PrecioEnAcuerdo.objects.en_acuerdo(self.producto, sucursal))

    def test_hay_acuerdo_para_cadena_nacional(self):
        acuerdo = AcuerdoFactory(nombre='Precio en Acuerdo',
                                 cadenas=[self.carrefour],
                                 region=self.caba)
        PrecioEnAcuerdoFactory(acuerdo=acuerdo,
                               producto=self.producto,
                               precio="18.9")
        suc1 = self.sucursales_carrefour[0]
        suc2 = self.sucursales_carrefour[1]
        suc3 = self.super_regional
        self.assertEqual(self.acuerdo(suc1),
                         [{'acuerdo__nombre': u'Precio en Acuerdo',
                           'precio': Decimal('18.90')}])
        self.assertEqual(self.acuerdo(suc2), [])
        self.assertEqual(self.acuerdo(suc3), [])

    def test_acuerdo_para_regional_de_cadena_chica(self):
        assert self.super_regional.cadena
        acuerdo = AcuerdoFactory(nombre='Precio en Acuerdo',
                                 sucursales=[self.super_regional],
                                 region=self.noa)
        PrecioEnAcuerdoFactory(acuerdo=acuerdo,
                               producto=self.producto,
                               precio="32.9")
        suc1 = self.sucursales_carrefour[0]
        suc2 = self.sucursales_carrefour[1]

        self.assertEqual(self.acuerdo(self.super_regional),
                         [{'acuerdo__nombre': u'Precio en Acuerdo',
                           'precio': Decimal('32.9')}])
        self.assertEqual(self.acuerdo(suc1), [])
        self.assertEqual(self.acuerdo(suc2), [])

    def test_acuerdo_para_super_regional_individual__sin_cadena(self):
        self.super_regional.cadena = None
        self.super_regional.save()
        acuerdo = AcuerdoFactory(nombre='Precio en Acuerdo',
                                 sucursales=[self.super_regional],
                                 region=self.noa)
        PrecioEnAcuerdoFactory(acuerdo=acuerdo,
                               producto=self.producto,
                               precio="32.9")

        suc1 = self.sucursales_carrefour[0]
        suc2 = self.sucursales_carrefour[1]

        self.assertEqual(self.acuerdo(self.super_regional),
                         [{'acuerdo__nombre': 'Precio en Acuerdo',
                           'precio': Decimal('32.9')}])
        self.assertEqual(self.acuerdo(suc1), [])
        self.assertEqual(self.acuerdo(suc2), [])
