# -*- coding: utf-8 -*-
"""
en esta aplicacion iran modelos y vistas auxiliares para
realizar tareas de saneamiento de dato masivo basadas
en usuarios voluntarios

la mayoria de los modelos contendran informacion que es
meramente auxiliar y a futuro podra ser eliminada
"""


from django.db import models
from django.contrib.auth.models import User
from model_utils.models import TimeStampedModel

from preciosa.precios.models import Categoria
from collections import Counter


class MapaCategoria(TimeStampedModel):
    """
    modelo auxiliar para resolver el ticket #64

    guardamos el aporte del usuario y cuando haya suficientes
    eligiremos la combinación origen->destino mas repetida
    """

    # no es la forma mas elegante pero si la más facil :)
    CAT_ORIGEN = Categoria.objects.get(nombre='A CLASIFICAR').get_children()

    origen = models.ForeignKey(Categoria,
                               limit_choices_to={'id__in': [c.id for c in CAT_ORIGEN]})
    # notar que todas las CAT de origen son depth=2 entonces
    # no hay peligro de colision
    destino = models.ForeignKey(Categoria, limit_choices_to={'depth': 2})
    user = models.ForeignKey(User)

    def __unicode__(self):
        return u'%s ---> %s' % (self.origen, self.destino)

    class Meta:
        # solo una eleccion por usuario por categoria
        unique_together = ('user', 'origen')

    @classmethod
    def resultados(cls):
        mapa = []
        for origen in cls.CAT_ORIGEN:
            counter = Counter([voto.destino for voto in
                               cls.objects.filter(origen=origen)])
            mejor_destino = counter.most_common(1)
            mapa.append((origen, mejor_destino))
        return mapa

