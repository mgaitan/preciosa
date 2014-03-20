# -*- coding: utf-8 -*-
"""
Import a file using the given adaptor.
The CSV could be a path (glob syntax is valid) or an URL

Available adaptors:

"""
import urllib2
import logging
from django.core.management.base import BaseCommand, CommandError
from preciosa.datos.adaptors import Adaptor
from glob import glob


logger = logging.getLogger(__name__)
if len(logger.handlers) == 0:
    logger = logging.getLogger('main')
    logger.setLevel('DEBUG')


class Command(BaseCommand):
    args = '<adaptor_name> <csv1> [<csv2> ...]'
    help = __doc__ + '    ' + '\n    '.join([cls.name for cls in
                                             Adaptor.__subclasses__()])

    def on_success(self, line):
        logger.debug("Created %s from line %i " % (repr(line.instance), line.line_number))

    def on_error(self, line):
        logger.error("Error on line %i: %s" % (line.line_number, line.error))

    def handle(self, *args, **options):
        if len(args) > 1:
            adaptor_name = args[0]
        else:
            raise CommandError(
                'You should give the adaptor name and a at least one '
                'csv input'
            )

        try:
            adaptor = [cls for cls in Adaptor.__subclasses__()
                       if cls.name.lower() == adaptor_name]
            assert len(adaptor) == 1
            adaptor = adaptor[0]
        except (AssertionError, IndexError):
            raise CommandError("There is no univocal adaptor named '%s'" % adaptor_name)

        for input_csv in args[1:]:
            if input_csv.startswith('http'):
                fh = urllib2.urlopen(input_csv)
                adaptor(fh, self.on_success, self.on_error).process()
            else:
                for csv_file in glob(input_csv):
                    adaptor(csv_file, self.on_success, self.on_error).process()
