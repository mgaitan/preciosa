# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models import Min

from model_utils import Choices
from model_utils.fields import MonitorField
from model_utils.models import TimeStampedModel
from image_cropping import ImageRatioField, ImageCropField
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

    @models.permalink
    def get_absolute_url(self):
        return ('lista_productos', (self.id, slugify(self.nombre)), {})

    @classmethod
    def por_clasificar(cls):
        return cls.objects.get(nombre='A CLASIFICAR').get_children()


class Producto(models.Model):
    UM_GRAMO = 'gr'
    UM_KILO = 'kg'
    UM_ML = 'ml'
    UM_L = 'l'
    UM_UN = 'unidad'
    UM_SM = 'SM'
    UM_MR = 'MR'

    UM_TRANS = {u'LT': 'l', u'UN': 'unidad'}

    UNIDADES_PESO = [UM_GRAMO, UM_KILO]
    UNIDADES_VOLUMEN = [UM_ML, UM_L]
    UNIDADES_CHOICES = Choices(UM_GRAMO, UM_KILO, UM_ML, UM_L,
                               UM_UN, UM_SM, UM_MR)

    descripcion = models.CharField(max_length=250)
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
                             upload_to='productos')
    acuerdos = models.ManyToManyField('Cadena', through='PrecioEnAcuerdo')

    def __unicode__(self):
        return self.descripcion

    @models.permalink
    def get_absolute_url(self):
        return ('detalle_producto',
                (self.categoria.id, slugify(self.categoria.nombre),
                 self.id, slugify(self.descripcion)), {})

    def mejor_precio(self):
        last_month = datetime.today() - timedelta(days=30)
        best = self.precio_set.filter(created__gte=last_month).aggregate(Min('precio'))
        return best['precio__min']


class Marca(models.Model):
    """
    Es el marca comercial de un producto.
    Ejemplo: Rosamonte
    """
    nombre = models.CharField(max_length=100, unique=True)
    logo = ImageCropField(null=True, blank=True,
                          upload_to='marcas')

    # size is "width x height"
    logo_cropped = ImageRatioField('logo', '150x125',
                                   verbose_name=u'Recortar logo')  # free_crop=True)
    logo_changed = MonitorField(monitor='logo')
    fabricante = models.ForeignKey('EmpresaFabricante', null=True, blank=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        unique_together = (('nombre', 'fabricante'))


class AbstractEmpresa(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    logo = ImageCropField(null=True, blank=True,
                          upload_to='empresas')
    logo_cropped = ImageRatioField('logo', '150x125',
                                   verbose_name=u'Recortar logo')  # free_crop=True)
    logo_changed = MonitorField(monitor='logo')

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

    def __unicode__(self):
        return u'%s: $ %s' % (self.producto, self.precio)


class PrecioEnAcuerdo(models.Model):
    producto = models.ForeignKey('Producto')
    cadena = models.ForeignKey('Cadena',
                               limit_choices_to={'cadena_madre__isnull': True})

    precio_norte = models.DecimalField(max_digits=5, decimal_places=2)
    precio_sur = models.DecimalField(max_digits=5, decimal_places=2)
