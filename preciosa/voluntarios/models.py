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

from preciosa.precios.models import (Cadena, Categoria, Marca,
                                    EmpresaFabricante, Sucursal)
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
    separar = models.BooleanField(verbose_name=u'Esta lista debería separarse en '
                                               u'varias categorías', default=False)
    comentario = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u'%s ---> %s' % (self.origen, self.destino)

    class Meta:
        # solo una eleccion por usuario por categoria
        unique_together = ('user', 'origen')

    @classmethod
    def resultados(cls):
        mapa = []
        for origen in Categoria.por_clasificar():
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


class EntidadCreadaVoluntario(TimeStampedModel):
    user = models.ForeignKey(User, editable=False)

    class Meta:
        abstract = True


class VotoVoluntario(TimeStampedModel):
    user = models.ForeignKey(User, editable=False)
    voto = models.IntegerField()

    class Meta:
        abstract = True


class MarcaEmpresaCreada(EntidadCreadaVoluntario):
    """un modelo para trackear la creacion de marcas
    o empresas por voluntarios"""
    marca = models.ForeignKey(Marca, editable=False, null=True)
    empresa = models.ForeignKey(EmpresaFabricante, editable=False, null=True)


class VotoMarcaEmpresaCreada(VotoVoluntario):
    u"""un usuario vota el item que creó otro """
    item = models.ForeignKey(MarcaEmpresaCreada, related_name='votos')


class SucursalCadenaCreada(EntidadCreadaVoluntario):
    u"""un modelo para trackear la creación de sucursales o cadenas
    de supermercados por voluntarios.

    """
    sucursal = models.ForeignKey(Sucursal, editable=False, null=True)
    cadena = models.ForeignKey(Cadena, editable=False, null=True)


class VotoSucursalCadenaCreada(VotoVoluntario):
    u"""un usuario vota el item que creó otro """
    item = models.ForeignKey(SucursalCadenaCreada, related_name='votos')
