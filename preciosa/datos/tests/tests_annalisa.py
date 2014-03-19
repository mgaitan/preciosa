from django.core.management import call_command
from django.test import TestCase
from decimal import Decimal
from mock import patch
from preciosa.precios.models import Producto
from preciosa.datos.management.commands.annalisa import Annalisa
from preciosa.precios.tests.factories import MarcaFactory, CategoriaFactory, ProductoFactory


class AnnalisaTestMixin(object):

    def setUp(self):
        self.patcher = patch('preciosa.datos.management.commands.annalisa.requests')
        self.api = Annalisa()

    def config(self, json_response):
        """json_response es el Mock de la respuesta json de Annalisa"""
        self.request_mock = self.patcher.start()
        self.request_mock.get.return_value.json.return_value = json_response
        self.addCleanup(lambda p: p.stop(), self.patcher)


class AnnalisaWrapperTestCase(AnnalisaTestMixin, TestCase):

    def test_unidad_volumen_litro_es_normalizada(self):
        self.config({'unidad_volumen': 'litro'})
        r = self.api.analyze('')
        self.assertEqual(r['unidad_medida'], Producto.UM_L)

    def test_unidad_volumen_ml_es_normalizada(self):
        self.config({'unidad_volumen': 'mililitro'})
        r = self.api.analyze('')
        self.assertEqual(r['unidad_medida'], Producto.UM_ML)

    def test_unidad_volumen_cc_es_normalizada(self):
        self.config({'unidad_volumen': 'centimetro cubico'})
        r = self.api.analyze('')
        self.assertEqual(r['unidad_medida'], Producto.UM_ML)

    def test_unidad_peso_gramo_normalizada(self):
        self.config({'unidad_peso': 'gramo'})
        r = self.api.analyze('')
        self.assertEqual(r['unidad_medida'], Producto.UM_GRAMO)

    def test_unidad_peso_kilo_normalizada(self):
        self.config({'unidad_peso': 'kilogramo'})
        r = self.api.analyze('')
        self.assertEqual(r['unidad_medida'], Producto.UM_KILO)

    def test_marca_es_normalizada(self):
        marca = MarcaFactory()
        self.config({'marcaid': marca.id})
        r = self.api.analyze('')
        self.assertEqual(r['marca'], marca)

    def test_categoria_normalizada(self):
        cat = CategoriaFactory(depth=3)
        self.config({'categoriaid': cat.id})
        r = self.api.analyze('')
        self.assertEqual(r['categoria'], cat)

    def test_categoria_debe_ser_nivel_3(self):
        cat = CategoriaFactory(depth=1)
        self.config({'categoriaid': cat.id})
        r = self.api.analyze('')
        self.assertNotIn('categoria', r)

    def test_peso_normalizado(self):
        self.config({'peso': 500})
        r = self.api.analyze('')
        self.assertEqual(r['contenido'], 500)

    def test_volumen_normalizado(self):
        self.config({'volumen': 500})
        r = self.api.analyze('')
        self.assertEqual(r['contenido'], 500)


def _(obj):
    """reload de la instancia"""
    return obj.__class__.objects.get(pk=obj.id)


class TestAnnalisaCommand(AnnalisaTestMixin, TestCase):

    def call(self, **kwargs):
        call_command('annalisa', verbosity=0, **kwargs)

    def test_producto_sin_marca_usa_annalisa(self):
        p = ProductoFactory(marca=None, unidad_medida=Producto.UM_L)
        marca = MarcaFactory()
        self.config({'marcaid': marca.id})
        self.call()
        self.assertEqual(_(p).marca, marca)

    def test_producto_con_marca_no_usa_annalisa_salvo_force(self):
        p = ProductoFactory()
        assert p.marca
        marca_org = p.marca
        marca2 = MarcaFactory()
        self.config({'marcaid': marca2.id})
        self.call()
        self.assertEqual(_(p).marca, marca_org)
        self.call(force_marca=True)
        self.assertEqual(_(p).marca, marca2)

    def test_producto_categoria_no_usa_annalisa_salvo_force(self):
        p = ProductoFactory()
        assert p.categoria
        cat_org = p.categoria
        cat2 = CategoriaFactory(depth=3)
        self.config({'categoriaid': cat2.id})
        self.call()
        self.assertEqual(_(p).categoria, cat_org)
        self.call(force_categoria=True)
        self.assertEqual(_(p).categoria, cat2)

    def test_producto_sin_unidad_usa_annalisa(self):
        p = ProductoFactory(unidad_medida=None)
        assert p.unidad_medida is None
        self.config({'unidad_peso': 'gramo'})
        self.call()
        self.assertEqual(_(p).unidad_medida, Producto.UM_GRAMO)

    def test_producto_con_unidad_no_usa_annalisa_salvo_force(self):
        p = ProductoFactory()
        assert p.unidad_medida != Producto.UM_GRAMO
        unidad_original = p.unidad_medida
        self.config({'unidad_peso': 'gramo'})
        self.call()
        self.assertEqual(_(p).unidad_medida, unidad_original)
        self.call(force_unidad_medida=True)
        self.assertEqual(_(p).unidad_medida, Producto.UM_GRAMO)

    def test_producto_sin_contenido_usa_annalisa(self):
        p = ProductoFactory(contenido=None)
        assert p.contenido is None
        self.config({'peso': 3.1})
        self.call()
        self.assertEqual(_(p).contenido, Decimal('3.1'))

    def test_producto_con_contenido_no_usa_annalisa_salvo_force(self):
        p = ProductoFactory()
        assert p.contenido and p.contenido != Decimal('2.1')
        contenido_original = p.contenido
        self.config({'volumen': 2.1})
        self.call()
        self.assertEqual(_(p).contenido, contenido_original)
        self.call(force_contenido=True)
        self.assertEqual(_(p).contenido, Decimal('2.1'))







