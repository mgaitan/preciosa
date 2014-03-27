# -*- coding: utf-8 -*-
import operator
from datetime import timedelta
from django.utils import timezone
from django.contrib.gis.db import models
from django.contrib.gis.db.models.query import GeoQuerySet
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.db.models import Min
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from cities_light.models import City
from django.db.models.signals import post_save
from annoying.functions import get_object_or_None
from model_utils import Choices
from model_utils.fields import MonitorField
from model_utils.models import TimeStampedModel
from easy_thumbnails.fields import ThumbnailerImageField
from image_cropping import ImageRatioField, ImageCropField
from treebeard.mp_tree import MP_Node
from djorm_pgtrgm import SimilarManager
from tools.utils import one
from tools.gis import geocode
from tools import texto


class Categoria(MP_Node):
    nombre = models.CharField(max_length=100)
    oculta = models.BooleanField(default=False)
    busqueda = models.CharField(max_length=300, editable=False)
    node_order_by = ['nombre']

    def reload(self):
        """ treebeard usa muchas raw queries que no actualizan automáticamente
        la instancia del modelo."""
        if self.id:
            return Categoria.objects.get(pk=self.id)
        return self

    def set_oculta(self, oculta):
        """cambia el estado de toda la rama a partir de la categoria actual"""
        self.oculta = oculta
        self.save()
        for sub in self.get_descendants():
            sub.oculta = oculta
            sub.save()

    def _actualizar_busqueda(self):
        busqueda = unicode(self).replace(' > ', ' ')
        self.busqueda = texto.normalizar(busqueda)
        super(Categoria, self).save(update_fields=['busqueda'])

    def save(self, *args, **kwargs):
        super(Categoria, self).save(*args, **kwargs)
        self._actualizar_busqueda()
        for sub in self.get_descendants():
            sub._actualizar_busqueda()

    def __unicode__(self):
        if not self.is_root():
            return unicode(self.get_parent()) + " > " + self.nombre
        return self.nombre

    class Meta:
        verbose_name = u"categoria"
        verbose_name_plural = u"categorias"

    @models.permalink
    def get_absolute_url(self):
        return ('lista_productos', (self.id, slugify(self.nombre)), {})

    @classmethod
    def por_clasificar(cls):
        return cls.objects.get(nombre='A CLASIFICAR').get_children()


class ProductoManager(SimilarManager):

    def buscar(self, q, limite=8):
        """Si q son digitos, busca por código de barra.
           otras cadenas, busca por similaridad e inclusión de
           palabras clave en la descripción"""

        if q.isdigit():
            productos = Producto.objects.filter(upc__startswith=q)[0:limite]
        else:
            q = texto.normalizar(q)
            words = q.split()
            palabras = Q(reduce(operator.and_,
                                (Q(busqueda__icontains=w) for w in words if len(w) > 2)))
            tiene_palabras = Producto.objects.filter(
                palabras).values_list('id',
                                      flat=True)
            similares = Producto.objects.filter_o(
                busqueda__similar=q).values_list('id',
                                                 flat=True)
            productos = Producto.objects.filter(Q(id__in=tiene_palabras) |
                                                Q(id__in=similares)).distinct()[0:limite]
        return productos


class Producto(models.Model):
    objects = ProductoManager()

    UM_GRAMO = 'gr'
    UM_KILO = 'kg'
    UM_ML = 'ml'        # 1ml == 1 cc
    UM_L = 'l'
    UM_UN = 'unidad'
    UM_M = 'm'
    UM_M2 = 'm2'

    UM_TRANS = {u'LT': UM_L, u'UN': UM_UN}

    UNIDADES_PESO = [UM_GRAMO, UM_KILO]
    UNIDADES_VOLUMEN = [UM_ML, UM_L]
    UNIDADES_CHOICES = Choices(UM_GRAMO, UM_KILO, UM_ML, UM_L,
                               UM_UN, UM_M, UM_M2)

    descripcion = models.CharField(max_length=250)
    busqueda = models.CharField(max_length=250, editable=False)

    upc = models.CharField(verbose_name=u"Código de barras",
                           max_length=13, unique=True, null=True, blank=True)
    categoria = models.ForeignKey('Categoria', related_name='productos')
    marca = models.ForeignKey('Marca', null=True, blank=True)
    contenido = models.DecimalField(max_digits=5, decimal_places=1,
                                    null=True, blank=True)
    unidad_medida = models.CharField(max_length=10,
                                     choices=UNIDADES_CHOICES, null=True, blank=True)
    notas = models.TextField(null=True, blank=True)
    foto = ThumbnailerImageField(null=True, blank=True, upload_to='productos')
    acuerdos = models.ManyToManyField('Cadena', through='PrecioEnAcuerdo')

    # TO DO: un queryset for defecto debe excluir los productos oculto=True
    # hacer una manager especial `objects_con_ocultos` que no los excluya
    # El buscador por codigo de barra (``if q.isdigit()``) deberá usar este
    # ultimo
    oculto = models.BooleanField(default=False,
                                 help_text=u"Por ejemplo: productos discontinuados."
                                           u"Sólo se encuentran por código de barra")
    unidades_por_lote = models.IntegerField(null=True, blank=True,
                                            help_text=u"Cuántas unidades vienen en un "
                                                      u" pack mayorista. Por ejemplo 12 "
                                                      u" (latas de tomate).")

    def __unicode__(self):
        return self.descripcion

    class Meta:
        verbose_name = u"producto"
        verbose_name_plural = u"productos"

    def save(self, *args, **kwargs):
        self.busqueda = texto.normalizar(self.descripcion)
        super(Producto, self).save(*args, **kwargs)

    def agregar_descripcion(self, descripcion, ignorar=False):
        try:
            with transaction.atomic():
                DescripcionAlternativa.objects.create(producto=self,
                                                      descripcion=descripcion)
        except IntegrityError:
            if not ignorar:
                raise

    @models.permalink
    def get_absolute_url(self):
        return ('detalle_producto',
                (self.categoria.id, slugify(self.categoria.nombre),
                 self.id, slugify(self.descripcion)), {})

    @property
    def foto_abs(self):
        if self.foto:
            return self.foto.url

    def mejor_precio(self):
        best = self.precios.aggregate(Min('precio'))
        return best['precio__min']

    def similares(self, maxnum=5):
        """devuelve un queryset de productos similares.
        (no incluye al producto en sí mismo)
        """
        qs = Producto.objects.exclude(id=self.id)
        return qs.filter_o(busqueda__similar=self.busqueda)[:maxnum]


class DescripcionAlternativa(models.Model):
    """
    Este modelo guarda otras denominaciones posibles de un mismo producto.
    Es útil para ampliar la *tabla de verdad* para hacer matching
    de productos provenientes de datasets sin UPC.

    """

    producto = models.ForeignKey('Producto', related_name='descripciones')
    descripcion = models.CharField(max_length=250, unique=True)
    busqueda = models.CharField(max_length=250)

    def save(self, *args, **kwargs):
        self.busqueda = texto.normalizar(self.descripcion)
        super(DescripcionAlternativa, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.descripcion

    class Meta:
        unique_together = (('producto', 'descripcion'))


class Marca(models.Model):

    """
    Es el marca comercial de un producto.
    Ejemplo: Rosamonte
    """
    fabricante = models.ForeignKey('EmpresaFabricante', null=True, blank=True)
    nombre = models.CharField(max_length=100, unique=True,
                              verbose_name=u"Nombre de la marca")
    logo = ImageCropField(null=True, blank=True,
                          upload_to='marcas')

    # size is "width x height"
    logo_cropped = ImageRatioField('logo', '150x125',
                                   verbose_name=u'Recortar logo', free_crop=True)
    logo_changed = MonitorField(monitor='logo', editable=False)

    def __unicode__(self):
        return self.nombre

    class Meta:
        unique_together = (('nombre', 'fabricante'))
        verbose_name = u"marca"
        verbose_name_plural = u"marcas"


class AbstractEmpresa(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    logo = ImageCropField(null=True, blank=True,
                          upload_to='empresas')
    logo_cropped = ImageRatioField('logo', '150x125',
                                   verbose_name=u'Recortar logo', free_crop=True)
    logo_changed = MonitorField(monitor='logo', editable=False)

    def __unicode__(self):
        return self.nombre

    class Meta:
        abstract = True


class Cadena(AbstractEmpresa):

    """Cadena de supermercados. Por ejemplo Walmart"""

    cadena_madre = models.ForeignKey('self', null=True, blank=True,
                                     help_text="Ej: Jumbo y Vea son de Cencosud")

    class Meta:
        verbose_name = u"cadena de supermercados"
        verbose_name_plural = u"cadenas de supermercados"


class EmpresaFabricante(AbstractEmpresa):
    pass


class SucursalQuerySet(GeoQuerySet):

    def buscar(self, q, limite=8):
        """
        Busca sucursales por palabras claves en ``q``.
        por ejemplo: ciudad, calle, cadena, etc.
        """
        q = texto.normalizar(q)
        words = q.split()
        palabras = Q(reduce(operator.and_,
                            (Q(busqueda__icontains=w) for w in words if len(w) > 2)))
        return self.filter(palabras)

    def alrededor_de(self, punto_o_lonlat, radio=15):
        """
        busca sucursales a la redonda.
        orderna por menor

        TO DO: hacer que este método se puede
        encadenar (es decir: método de manager o queryset)
        """
        if not isinstance(punto_o_lonlat, Point):
            punto_o_lonlat = Point(*punto_o_lonlat)
        circulo = (punto_o_lonlat, D(km=radio))
        qs = self.filter(ubicacion__distance_lte=circulo)
        return qs.distance(punto_o_lonlat).order_by('distance')


class SucursalManager(models.GeoManager):

    def get_queryset(self):
        return SucursalQuerySet(self.model, using=self._db)

    def buscar(self, q, limite=8):
        return self.get_queryset().buscar(q, limite)

    def alrededor_de(self, punto_o_lonlat, radio):
        return self.get_queryset().alrededor_de(punto_o_lonlat, radio)


class Sucursal(models.Model):
    objects = SucursalManager()

    nombre = models.CharField(max_length=100, null=True, blank=True,
                              help_text="Denominación común. Ej: Jumbo de Alberdi")
    # direccion sólo puede ser nulo para sucursales online
    direccion = models.CharField(max_length=200, null=True, blank=True)
    ciudad = models.ForeignKey('cities_light.City')
    cp = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=100, null=True, blank=True)

    horarios = models.TextField(verbose_name='Notas',
                                null=True, blank=True,
                                help_text="Ej: Horarios de atención")
    cadena = models.ForeignKey('Cadena', related_name='sucursales',
                               null=True, blank=True,
                               help_text='Dejar en blanco si es un comercio único')

    ubicacion = models.PointField(srid=4326, null=True, blank=True,)
    online = models.BooleanField(default=False,
                                 help_text='Es una sucursal online, no física')
    url = models.URLField(max_length=200, null=True, blank=True)
    busqueda = models.CharField(max_length=300, editable=False)

    def _actualizar_busqueda(self, commit=True):
        """denormalizacion de varios atributos relacionados para
        agilizar una busqueda de sucursales por palabras claves"""

        claves = []
        if self.nombre:
            nombre = texto.normalizar(self.nombre)
            # quitamos palabras comunes
            nombre = nombre.replace('sucursal', '').replace('supermercado', '')
            claves.append(nombre)

        if self.cadena:
            claves.append(texto.normalizar(self.cadena.nombre))

        if self.ciudad:
            claves.append(texto.normalizar(self.ciudad.name))
            if self.ciudad.region:
                claves.append(texto.normalizar(self.ciudad.region.name))

        if self.direccion:
            claves.append(texto.normalizar(self.direccion))

        self.busqueda = " ".join(claves)
        if commit:
            super(Sucursal, self).save(update_fields=['busqueda'])

    def save(self, *args, **kwargs):
        self._actualizar_busqueda(False)
        super(Sucursal, self).save(*args, **kwargs)

    @property
    def lat(self):
        if self.ubicacion:
            return self.ubicacion.y
        return None

    @property
    def lon(self):
        if self.ubicacion:
            return self.ubicacion.x
        return None

    def get_geocode_data(self):
        return geocode(self.ciudad, self.direccion)

    def cercanas(self, radio=None, misma_cadena=False):
        """
        Devuelve un listado de cadenas cercanas.
        Si radio es None, se considera toda la ciudad. Si es un numero
        es "a la redonda" a partir de la posicion de la sucursal actual.

        El orden es por cercania, si puede calcularse.

        misma_cadena condiciona a otras sucursales de la misma
        cadena
        """
        otras = Sucursal.objects.all()
        if self.id:
            otras = otras.exclude(id=self.id)

        if misma_cadena:
            otras = otras.filter(cadena=self.cadena)

        if radio and self.ubicacion:
            otras = otras.alrededor_de(self.ubicacion, radio)
        else:
            otras = otras.filter(ciudad=self.ciudad)

        if self.ubicacion:
            otras = otras.distance(self.ubicacion).order_by('distance')

        return otras

    def clean(self):
        if not any((self.cadena, self.nombre)):
            raise ValidationError(
                u'Indique la cadena o el nombre del comercio')

        if not self.online and not self.direccion:
            raise ValidationError(
                u'Una sucursal física debe tener dirección')

        if self.online and not self.url:
            raise ValidationError(
                u'La url es obligatoria para sucursales online')

        if not one((self.direccion, self.online)):
            raise ValidationError(u'La sucursal debe ser online '
                                  u'o tener direccion física, pero no ambas')

        if (self.ubicacion and self.cadena and
                self.cercanas(radio=0.05, misma_cadena=True).exists()):
            raise ValidationError(
                u'Hay una sucursal de la misma cadena a menos de 50 metros')

    def __unicode__(self):
        return u"%s (%s)" % (self.nombre or self.cadena, self.direccion or self.url)

    class Meta:
        unique_together = (('direccion', 'ciudad'))
        verbose_name = u"sucursal"
        verbose_name_plural = u"sucursales"


class PrecioManager(models.Manager):

    def _registro_precio(self, qs, distintos=True):
        """dado un qs de Precio, devuelve una lista los precios y
        la fecha de registro, ordenados de más nuevo a más viejo.

        Si distintos es True, sólo devuelve la primera fecha
        en que un precio cambió
        """
        if distintos:
            qs = qs.distinct('precio')
        return sorted(qs, key=lambda i: i.created, reverse=True)

    def historico(self, producto, sucursal, dias=None, distintos=True):
        """
        dado un producto y sucursal
        devuelve una lista de precios y la fecha de su registro
        ordenados de la mas nueva a las más vieja.

        por defecto solo muestra precios distintos.
        Para un historial completo (ejemplo, para graficar
        una curva de evolucion de precio), asigar ``distintos=False``

        dias filtra a registros mas nuevos a los X dias.

        """
        qs = super(PrecioManager, self).get_queryset()
        qs = qs.filter(producto=producto, sucursal=sucursal)
        if dias:
            desde = timezone.now() - timedelta(days=dias)
            qs = qs.filter(created__gte=desde)
        # se ordenará de más nuevo a más viejo, pero
        return self._registro_precio(qs, distintos)

    def mas_probables(self, producto, sucursal, dias=None, radio=10):
        """
        Cuando no hay datos especificos de un
        producto para una sucursal (:meth:`historico`),
        debe ofrecerse un precio más probable. Se calcula

         - Precio con más coincidencias para el producto en otras sucursales
           de la misma cadena en la ciudad y/o un radio de distancia si es dado

         - En su defecto, precio online de la cadena
        """
        qs = self.historico(producto, sucursal, dias)
        if len(qs) > 0:
            return qs

        qs = super(PrecioManager, self).get_queryset()

        # precios para sucursales de la misma cadena de la ciudad
        cercanas_ciudad = sucursal.cercanas(misma_cadena=True).values_list('id',
                                                                           flat=True)
        if radio:
            cercanas_radio = sucursal.cercanas(radio=radio,
                                               misma_cadena=True).values_list('id',
                                                                              flat=True)
        else:
            cercanas_radio = []

        cercanas = set(list(cercanas_ciudad) + list(cercanas_radio))
        qs = qs.filter(producto=producto,
                       sucursal__id__in=cercanas).distinct('precio')
        if qs.exists():
            return self._registro_precio(qs)

        qs = super(PrecioManager, self).get_queryset()
        qs = qs.filter(producto=producto,
                       sucursal__cadena=sucursal.cadena,
                       sucursal__online=True).distinct('precio')
        # precios online
        if qs.exists():
            return self._registro_precio(qs)
        return []

    def mejores(self, producto, ciudad=None, punto_o_sucursal=None,
                radio=None, dias=None, limite=5):
        """
        devuelve una lista de instancias Precio para el producto,
        ordenados por menor precio (importe) para
        un determinado producto y un radio de distancia o ciudad.

        Sólo considera el último precio en cada sucursal.
        """
        if not one((ciudad, radio)):
            raise ValueError(
                'Debe proveer una ciudad o un radio en kilometros')

        if one((radio, punto_o_sucursal)):
            raise ValueError(
                'Si se especifica radio debe proveer el punto o sucursal')

        qs = super(PrecioManager,
                   self).get_queryset().filter(producto=producto, activo__isnull=False)

        if dias:
            desde = timezone.now() - timedelta(days=dias)
            qs = qs.filter(created__gte=desde)

        if radio:
            if isinstance(punto_o_sucursal, Sucursal):
                punto = punto_o_sucursal.ubicacion
            else:
                punto = punto_o_sucursal
            cercanas = Sucursal.objects.filter(ubicacion__distance_lte=(punto,
                                                                        D(km=radio)))
            cercanas = cercanas.values_list('id', flat=True)
            qs = qs.filter(sucursal__id__in=cercanas).distinct(
                'sucursal')[:limite]
        elif ciudad:
            if isinstance(ciudad, City):
                ciudad = ciudad.id
            qs = qs.filter(sucursal__ciudad__id=ciudad).distinct(
                'sucursal')[:limite]
        if qs.exists():
            return sorted(qs, key=lambda i: i.precio)
        return []


class Precio(TimeStampedModel):
    objects = PrecioManager()

    producto = models.ForeignKey('Producto', related_name='precios')
    sucursal = models.ForeignKey('Sucursal')
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    usuario = models.ForeignKey(User, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Precio, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s: $ %s' % (self.producto, self.precio)

    class Meta:
        verbose_name = u"precio"
        verbose_name_plural = u"precios"


class PrecioActivo(models.Model):

    """cada vez que se agrega un precio,
    es el precio activo de ese producto para la sucursal"""

    producto = models.ForeignKey('Producto', related_name='precios_activos')
    sucursal = models.ForeignKey('Sucursal')
    precio = models.ForeignKey(Precio, related_name='activo')

    class Meta:
        unique_together = ('producto', 'sucursal', 'precio')


def actualizar_precio_activo(sender, **kwargs):
    if kwargs['created']:
        precio = kwargs['instance']
        activo = get_object_or_None(PrecioActivo, producto=precio.producto,
                                    sucursal=precio.sucursal)
        if activo:
            activo.precio = precio
            activo.save(update_fields=['precio'])
        else:
            PrecioActivo.objects.create(producto=precio.producto,
                                        sucursal=precio.sucursal,
                                        precio=precio)


post_save.connect(actualizar_precio_activo, sender=Precio)


class PrecioEnAcuerdo(models.Model):
    producto = models.ForeignKey('Producto')
    cadena = models.ForeignKey('Cadena',
                               limit_choices_to={'cadena_madre__isnull': True})

    precio_norte = models.DecimalField(max_digits=5, decimal_places=2)
    precio_sur = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = u"precio en acuerdo"
        verbose_name_plural = u"precios en acuerdo"
