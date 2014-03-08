# -*- coding: utf-8 -*-
from tools.utils import UnicodeDictReader
from preciosa.precios.models import Producto, DescripcionAlternativa

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    # TODO: possible arguments: 
    # - whether to consider 'Des' products.
    # - whether to add alt. descriptions
    args = '<path-to-art.csv-file>'
    help = 'Integracion de productos de art.csv.'
    
    UNIDADES_MAPPING = {'Kg': Producto.UM_KILO,
                        'Gr': Producto.UM_GRAMO,
                        'Cm': Producto.UM_ML,
                        'Cc': Producto.UM_ML,
                        'Ml': Producto.UM_ML,
                        'Lt': Producto.UM_L,
                        'Un': Producto.UM_UN,
                        'Mt': Producto.UM_M,
                        'M2': Producto.UM_M2
                       }
    
    def handle(self, *args, **options):
        # XXX: load all the products in memory
        products = Producto.objects.all()
        #upcs = set(p.upc.lstrip('0') for p in products)
        upcs_dict = dict((p.upc.lstrip('0'), p) for p in products)
        
        filename = args[0]
        f = open(filename)
        reader = UnicodeDictReader(f, encoding='iso-8859-1', delimiter=';')
        
        known_products = 0
        new_das = 0
        
        for row in reader:
            #print 'Processing {0}'.format(row['Cod Scanner'])
            
            if row['HD'] == 'Hab':
                upc = row['Cod Scanner']
                
                # obtain value for unidad_medida
                um = row[' ']
                assert um in Command.UNIDADES_MAPPING # known for 'Hab' products
                um2 = Command.UNIDADES_MAPPING[um]
                # obtain value for contenido
                cont = row['Present']
                
                if upc in upcs_dict:
                    known_products += 1
                    
                    # add alternative description for existing products
                    # TODO: check if alternative description is not already there
                    p = upcs_dict[upc]
                    _, b = DescripcionAlternativa.objects.get_or_create(
                                                producto=p, 
                                                descripcion=row['Descripcion'])
                    if b:
                        new_das += 1
                    
                    # OLD: break if previous unidad_medida is different
                    #assert p.unidad_medida in [None, um2], 'La unidad no coincide para {0}.'.format(upc)
                    
                    if cont:
                        # overwrite values if cont is not empty
                        p.unidad_medida = um2
                        p.contenido = cont
                    
                    # p.contenido may not validate, but it does, at least with 
                    # 'Hab' products.
                    p.save()
                else:
                    # TODO: new product! add it.
                    pass
                    
        # TODO: log properly
        print 'Found {0} new products'.format(known_products)
        print 'Added {0} new alternative descriptions'.format(new_das)

