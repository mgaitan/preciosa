# -*- coding: utf-8 -*-
import os.path

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from model_utils import Choices
from model_utils.models import TimeStampedModel
from treebeard.mp_tree import MP_Node


class Categoria(MP_Node):
    nombre = models.CharField(max_length=100)
    node_order_by = ['nombre']

    def reload(self):
        if self.id:
            return Categoria.objects.get(pk=self.id)
        return self

    def __unicode__(self):
        if not self.is_root():
            return unicode(self.get_parent()) + " > " + self.nombre
        return self.nombre


class Producto(models.Model):
    UM_GRAMO = 'gr'
    UM_KILO = 'kg'
    UM_ML = 'ml'
    UM_L = 'l'
    UM_UN = 'unidad'
    UNIDADES_PESO = [UM_GRAMO, UM_KILO]
    UNIDADES_VOLUMEN = [UM_ML, UM_L]
    UNIDADES_CHOICES = Choices(UM_GRAMO, UM_KILO, UM_ML, UM_L, UM_UN)

    descripcion = models.CharField(max_length=100)
    upc = models.CharField(verbose_name=u"Código de barras",
                           max_length=13, unique=True, null=True, blank=True)
    categoria = models.ForeignKey('Categoria')
    marca = models.ForeignKey('Marca', null=True, blank=True)
    contenido = models.DecimalField(max_digits=5, decimal_places=1,
                                    null=True, blank=True)
    unidad_medida = models.CharField(max_length=10,
                                     choices=UNIDADES_CHOICES, null=True, blank=True)
    notas = models.TextField(null=True, blank=True)
    foto = models.ImageField(null=True, blank=True,
                             upload_to=os.path.join(settings.MEDIA_ROOT, 'productos'))
    acuerdos = models.ManyToManyField('Cadena', through='PrecioEnAcuerdo')

    def __unicode__(self):
        return self.descripcion


class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(null=True, blank=True,
                             upload_to=os.path.join(settings.MEDIA_ROOT, 'marcas'))
    fabricante = models.ForeignKey('EmpresaFabricante', null=True, blank=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        unique_together = (('nombre', 'fabricante'))


class AbstractEmpresa(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(null=True, blank=True,
                             upload_to=os.path.join(settings.MEDIA_ROOT, 'empresas'))

    def __unicode__(self):
        return self.nombre

    class Meta:
        abstract = True


class Cadena(AbstractEmpresa):
    """Cadena de supermercados. Por ejemplo Walmart"""

    cadena_madre = models.ForeignKey('self', null=True, blank=True,
                                     help_text="Jumbo y Vea son de Cencosud")


class EmpresaFabricante(AbstractEmpresa):
    pass


class Sucursal(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True,
                              help_text="Denominación común. Ej: Jumbo de Alberdi")
    direccion = models.CharField(max_length=120)
    ciudad = models.ForeignKey('cities_light.City')
    cp = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=100, null=True, blank=True)
    horarios = models.TextField(null=True, blank=True)
    cadena = models.ForeignKey('Cadena', related_name='sucursales',
                               null=True, blank=True,
                               help_text='Dejar en blanco si es un comercio único')

    def clean(self):
        if not self.cadena and not self.nombre:
            raise models.ValidationError('Indique la cadena o el nombre del comercio')

    def __unicode__(self):
        return u"%s (%s)" % (self.cadena or self.nombre, self.direccion)

    class Meta:
        unique_together = (('direccion', 'ciudad'))


class Precio(TimeStampedModel):
    producto = models.ForeignKey('Producto')
    sucursal = models.ForeignKey('Sucursal')
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    usuario = models.ForeignKey(User, null=True, blank=True)


class PrecioEnAcuerdo(models.Model):
    producto = models.ForeignKey('Producto')
    cadena = models.ForeignKey('Cadena',
                               limit_choices_to={'cadena_madre__isnull': True})

    precio_norte = models.DecimalField(max_digits=5, decimal_places=2)
    precio_sur = models.DecimalField(max_digits=5, decimal_places=2)
