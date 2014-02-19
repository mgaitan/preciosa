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

from preciosa.precios.models import Categoria, Marca, EmpresaFabricante
from collections import Counter


class MapaCategoria(TimeStampedModel):
    """
    modelo auxiliar para resolver el ticket #64

    guardamos el aporte del usuario y cuando haya suficientes
    eligiremos la combinación origen->destino mas repetida
    """

    origen = models.ForeignKey(Categoria, related_name='mapeo_origen')
    # notar que todas las CAT de origen son depth=2 entonces
    # no hay peligro de colision
    destino = models.ForeignKey(Categoria,
                                related_name='mapeo_destino',
                                verbose_name=u"Yo la asociaría con...",
                                limit_choices_to={'depth': 3})
    user = models.ForeignKey(User, editable=False)

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

    @classmethod
    def categorizables_por_voluntario(cls, user):
        ya_hechas = MapaCategoria.objects.filter(user=user).values_list(
            'origen_id', flat=True)
        return Categoria.por_clasificar().exclude(id__in=ya_hechas)


class MarcaEmpresaCreada(TimeStampedModel):
    """un modelo para trackear la creacion de marcas
    o empresas por voluntarios"""
    user = models.ForeignKey(User, editable=False)
    marca = models.ForeignKey(Marca, editable=False, null=True)
    empresa = models.ForeignKey(EmpresaFabricante, editable=False, null=True)


class VotoMarcaEmpresaCreada(TimeStampedModel):
    """un usuario vota el item que creó otro """
    user = models.ForeignKey(User, editable=False)
    item = models.ForeignKey(MarcaEmpresaCreada)
    voto = models.IntegerField()
