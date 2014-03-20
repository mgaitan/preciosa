from collections import namedtuple
import unicodecsv
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point
from cities_light.models import City
from preciosa.precios.models import Sucursal, Cadena


SUCURSAL_COLS = ['nombre',
                 'cadena_nombre',
                 'cadena_id',
                 'direccion',
                 'ciudad',
                 'ciudad_relacionada_id',
                 'provincia',
                 'lon',
                 'lat',
                 'telefono',
                 'url',
                 'horarios']


PRODUCTO_COLS = ['id',           # opcional
                 'upc',          # req
                 'descripcion',  # req
                 'marca',        # opcional. La marca "probable" como nombre
                 'marca_id',     # opcional. si es conocida, el id de la marca
                 'categoria',    # opcional. La categoria "probable" como nombre
                 'categoria_id',    # opcional. si es conocida, el id de la marca
                 'contenido',    # opcional, numero
                 'unidad_medida',   # opcional. Producto.UNIDADES_CHOICES
                 'unidades_por_lote',   # opcional: cuantos productos
                                        #vienen en un pack mayorista
                 'oculto',      # opcional.default: false
                 'foto',        # opcional  path relativo, relativo al csv o url
                                # de un thumbnail del producto
                 ]

PRECIO_COLS = PRODUCTO_COLS + ['id_sucursal',                # requerido
                               'precio',                     # requerido
                               'fecha_relevamiento',         # opcional.
                                                             # sobre escribe el created
                               ]


LineSuccess = namedtuple('LineSuccess',
                         field_names=['line_number', 'line', 'instance'])
LineError = namedtuple('LineError',
                       field_names=['line_number', 'line', 'error'])


class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class Adaptor(object):
    SKIP_ON_ERROR = False
    HAS_HEADERS = True

    def __init__(self, input_csv, on_success=None, on_error=None):
        """
        Iniatilize the Adaptor instance, with a CSV input.
        could be a filename or a filehandler.

        on_success and on_error are optional callbacks invoked
        after the process of each line.

        They receive the LineSuccess / LineError object respectively
        """
        if not hasattr(self, 'HEADERS'):
            raise ValueError('You should define the HEADERS of the CSV')
        if not hasattr(self, 'MODEL'):
            raise ValueError('Define the Model!')

        if not hasattr(input_csv, 'read'):
            input_csv = open(input_csv, 'rb')
        self._on_success = on_success if callable(on_success) else lambda l: None
        self._on_error = on_error if callable(on_error) else lambda l: None
        self._csv_fh = input_csv

    def process(self, input_csv=None):
        """
        process each line in the input file.
        return a tuple (succesess, errors)
        """
        successes = []
        errors = []
        reader = unicodecsv.DictReader(self._csv_fh,
                                       fieldnames=self.HEADERS)
        if self.HAS_HEADERS:
            reader.next()
        for i, line in enumerate(reader):
            line_number = i + 1 if self.HAS_HEADERS else i
            data = self.process_line(line)
            try:
                instance = self.create_instance(**data)
            except ValidationError as e:
                le = LineError(line_number, line, unicode(e))
                errors.append(le)
                self._on_error(le)
                if self.SKIP_ON_ERROR:
                    continue
                raise
            ls = LineSuccess(line_number, line, instance)
            successes.append(ls)
            self._on_success(ls)
        return successes, errors

    @ClassProperty
    @classmethod
    def name(cls):
        return getattr(cls, 'NAME', cls.__name__).lower()

    @classmethod
    def import_data(cls, data):
        """drop-in compatibility with django-adaptors
        useful to work with django-devour
        """
        return cls(data).process()

    def process_line(self, line):
        """override in your subclass"""
        return line

    def create_instance(self, **data):
        instance = self.MODEL(**data)
        instance.full_clean()
        instance.save()
        return instance


class Sucursal(Adaptor):
    MODEL = Sucursal
    HEADERS = SUCURSAL_COLS
    SKIP_ON_ERROR = True

    def process_line(self, line):
        data = {}
        for field in ['nombre', 'direccion', 'telefono', 'url', 'horarios']:
            data[field] = line[field]
        if line['cadena_id']:
            data['cadena'] = Cadena.objects.get(id=line['cadena_id'])
        try:
            data['ciudad'] = City.objects.get(id=int(line['ciudad_relacionada_id']))
        except City.DoesNotExist as e:
            raise ValidationError(str(e))
        if line['lat'] and line['lon']:
            data['ubicacion'] = Point(float(line['lon']), float(line['lat']))
        return data
