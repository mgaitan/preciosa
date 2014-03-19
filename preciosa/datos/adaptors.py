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

LineError = namedtuple('LineError', field_names=['line_number', 'line', 'error'])


class Adaptor(object):
    SKIP_ON_ERROR = False
    HAS_HEADERS = True

    def __init__(self, filename):
        if not hasattr(self, 'HEADERS'):
            raise ValueError('You should define the HEADERS of the CSV')
        if not hasattr(self, 'MODEL'):
            raise ValueError('Define the Model!')

        self._csv_file = filename

    def process(self):
        csv_file = open(self._csv_file)
        instances = []
        errors = []
        reader = unicodecsv.DictReader(csv_file, fieldnames=self.HEADERS)
        if self.HAS_HEADERS:
            reader.next()
        for i, line in enumerate(reader):
            data = self.process_line(line)
            try:
                instance = self.create_instance(**data)
            except ValidationError as e:
                errors.append(LineError(i + 1 if self.HAS_HEADERS else i,
                                        line, unicode(e)))
                if self.SKIP_ON_ERROR:
                    continue
                raise
            instances.append(instance)
        return instances, errors

    @classmethod
    def import_data(cls, data):
        return cls(data).process()

    def process_line(self, line):
        """override in your subclass"""
        return line

    def create_instance(self, **data):
        instance = self.MODEL(**data)
        instance.full_clean()
        instance.save()
        return instance


class SucursalCSVModel(Adaptor):
    MODEL = Sucursal
    HEADERS = SUCURSAL_COLS
    SKIP_ON_ERROR = True

    def process_line(self, line):
        data = {}
        for field in ['nombre', 'direccion', 'telefono', 'url', 'horarios']:
            data[field] = line[field]
        if line['cadena_id']:
            data['cadena'] = Cadena.objects.get(id=line['cadena_id'])
        data['ciudad'] = City.objects.get(id=int(line['ciudad_relacionada_id']))
        if line['lat'] and line['lon']:
            data['ubicacion'] = Point(float(line['lon']), float(line['lat']))
        return data




