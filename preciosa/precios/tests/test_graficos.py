from django.test import TestCase
from datetime import timedelta, date
from django.utils import timezone
from decimal import Decimal
from preciosa.precios.models import Precio
from preciosa.precios.tests.factories import (SucursalFactory,
                                              ProductoFactory,
                                              PrecioFactory)

from preciosa.precios.graficos import graphdata_sucursal, to_flottimestamp,\
                                    graphdata_comparando_sucursales


class TestPrecioHistorico(TestCase):

    def setUp(self):
        self.sucursal1 = SucursalFactory()
        self.sucursal2 = SucursalFactory()
        self.sucursal1.online = True
        self.sucursal2.online = True
        self.sucursal1.save()
        self.sucursal2.save()

        self.producto = ProductoFactory()

        self.hoy = hoy = date.today()
        self.ayer = ayer = hoy - timedelta(days=1)
        self.anteayer = anteayer = ayer - timedelta(days=1)
        self.hace10dias = hace10dias = hoy - timedelta(days=10)
        self.hace20dias = hace20dias = hoy - timedelta(days=20)

        sucursal = self.sucursal1
        self.add('10.56', hoy, sucursal)
        self.add('11.20', ayer, sucursal)
        self.add('11.20', ayer, sucursal)
        self.add('11.30', anteayer, sucursal)
        self.add('9.12', hace10dias, sucursal)
        self.add('8.12', hace20dias, sucursal)

        sucursal = self.sucursal2
        self.add('9.56', hoy, sucursal)
        self.add('10.20', ayer, sucursal)
        self.add('11.20', ayer, sucursal)
        self.add('10.30', anteayer, sucursal)
        self.add('8.12', hace10dias, sucursal)
        self.add('9.12', hace20dias, sucursal)

    def add(self, precio, created, sucursal, **kwargs):
        return PrecioFactory(sucursal=sucursal,
                             producto=self.producto,
                             precio=precio,
                             created=created,
                             **kwargs)

    def test_graficos_una_sucursal(self):
        sucursal = self.sucursal1

        graph_data = graphdata_sucursal(sucursal, self.producto, dias=15)
        self.assertEqual(graph_data,
            {
                "data":
                    [[to_flottimestamp(self.hoy), 10.56],
                     [to_flottimestamp(self.ayer), 11.20],
                     [to_flottimestamp(self.ayer), 11.20],
                     [to_flottimestamp(self.anteayer), 11.30],
                     [to_flottimestamp(self.hace10dias), 9.12]
                    ],
                "label": sucursal.nombre
            }
        )

        graph_data = graphdata_sucursal(sucursal, self.producto, dias=5)
        self.assertEqual(graph_data,
            {
                "data":
                    [[to_flottimestamp(self.hoy), 10.56],
                     [to_flottimestamp(self.ayer), 11.20],
                     [to_flottimestamp(self.ayer), 11.20],
                     [to_flottimestamp(self.anteayer), 11.30],
                    ],
                "label": sucursal.nombre
            }
        )

        graph_data = graphdata_sucursal(sucursal, self.producto, dias=30)
        self.assertEqual(graph_data,
            {
                "data":
                    [[to_flottimestamp(self.hoy), 10.56],
                     [to_flottimestamp(self.ayer), 11.20],
                     [to_flottimestamp(self.ayer), 11.20],
                     [to_flottimestamp(self.anteayer), 11.30],
                     [to_flottimestamp(self.hace10dias), 9.12],
                     [to_flottimestamp(self.hace20dias), 8.12]
                    ],
                "label": sucursal.nombre
            }
        )

    def test_grafico_sucursales_comparadas(self):
        graph_data = graphdata_comparando_sucursales(self.producto, dias=15)
        self.assertEqual(graph_data,
            [{
                "data":
                    [[to_flottimestamp(self.hoy), 10.56],
                     [to_flottimestamp(self.ayer), 11.20],
                     [to_flottimestamp(self.ayer), 11.20],
                     [to_flottimestamp(self.anteayer), 11.30],
                     [to_flottimestamp(self.hace10dias), 9.12]
                    ],
                "label": self.sucursal1.nombre
            },
            {
                "data":
                    [[to_flottimestamp(self.hoy), 9.56],
                     [to_flottimestamp(self.ayer), 10.20],
                     [to_flottimestamp(self.ayer), 11.20],
                     [to_flottimestamp(self.anteayer), 10.30],
                     [to_flottimestamp(self.hace10dias), 8.12]
                    ],
                "label": self.sucursal2.nombre
            }
            ]
        )
        pass

    def test_grafico_promedio_sucursales(self):
        pass
