# from django.core.management import call_command
from django.test import TestCase
from mock import patch
from preciosa.precios.management.commands.annalisa import Annalisa


class AnnalisaTestCase(TestCase):

    def setUp(self):
        self.patcher = patch('preciosa.precios.management.commands.annalisa.requests')

    def tearDown(self):
        self.patcher.stop()

    def config(self, json_response):
        mock = self.patcher.start()
        mock.get.return_value.json.return_value = json_response

    def test_mycommand(self):
        " Test my custom command."
        self.config({'unidad_volumen': 'litro'})
        api = Annalisa()
        r = api.analyze('zaraza')
        self.assertEqual(r['unidad_medida'], 'l')

