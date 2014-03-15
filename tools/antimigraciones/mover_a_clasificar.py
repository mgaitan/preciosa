# -*- coding: utf-8 -*-
"""
script para el ticket #200
basado en estos resultados de votacion de voluntarios

https://github.com/mgaitan/preciosa/issues/200#issuecomment-37727675

mas funciones de metaprogramacion
"""
from django.db import transaction
from django.utils.text import slugify
from preciosa.precios.models import Categoria


def _generar_codigo_de_destinos_para(cat_depth2):
    """un helper para generar codigos de destino"""
    line = "%s = Categoria.objects.get(id=%d)   #%s "
    lines = []
    destinos = []
    for cat in cat_depth2.get_children():
        destino = cat.busqueda.split()[-1]
        destinos.append(destino)
        lines.append(line % (destino, cat.id, cat.nombre))

    mapa = ", ".join("(%s, %s)" % s for s in destinos)
    return '\n    '.join(lines), mapa


def metamagia():
    """un intento de genera el codigo necesario para toda la zaraza
    de mudanzas"""

    # resultado de los voluntarios
    mapa = {773: 643, 774: 297, 775: 657, 776: 598, 777: None,
            778: 282, 779: 706, 780: 226, 781: 628, 782: 661,
            783: 387, 784: 360, 785: 413, 786: 688, 787: 650,
            788: 287, 789: 637, 790: 600, 791: 702, 792: 612, 793: 589,
            794: 292, 795: 625, 796: 658, 797: 380, 798: 677, 799: 434,
            800: 634, 801: 413, 802: 360, 803: 654, 804: 459, 805: 682,
            806: 277, 807: 627, 808: 405, 809: 378, 810: 352, 811: 303,
            812: 550, 813: 391, 815: 284, 816: 657, 817: 303, 818: 384,
            819: 622, 820: 445, 821: 637, 822: 266, 823: None, 824: 630,
            825: None, 826: 666, 827: 416, 828: 613, 829: 362, 830: 316,
            831: 584, 832: 657, 833: 582, 834: 274, 835: 406, 836: 478,
            837: 292, 838: 289, 839: 351, 840: 291, 841: 296, 842: 697,
            844: 675, 845: 621, 846: 464, 847: 469, 848: 303, 849: None,
            850: 294, 851: 643, 852: 651, 853: 521, 854: 291, 855: 626,
            856: None, 857: 306, 858: 622, 860: 501, 861: 672, 862: 575,
            863: 298, 864: 352, 865: None, 866: 428, 867: 292, 868: 643,
            869: 690, 870: 435, 871: 654, 872: 260, 873: 374, 874: 697,
            875: None, 876: 456, 877: 314, 878: 359, 879: 606, 880: 293,
            881: 248, 882: 506, 883: None, 884: 292, 885: 261, 886: 308,
            887: 270, 888: 661, 889: 292, 890: 579, 891: 678, 892: 472,
            893: 575, 894: 607, 895: 243, 896: None, 897: 572, 898: None,
            899: 576, 900: 404, 901: 601, 902: 390, 903: 643, 904: 234,
            905: 283, 906: 378, 907: 644, 908: 357, 909: 290, 910: 511,
            911: 290, 912: None, 913: 593, 914: 676, 915: None, 916: 315,
            917: 665, 918: 388, 919: 278, 920: 642, 921: 636, 922: 610,
            923: 374, 924: 599, 925: 304, 926: 635, 927: 629, 928: 374,
            929: 457, 930: 411, 931: 354, 932: 414, 933: 449, 934: 279,
            935: 356, 936: 444, 937: None, 938: 591, 939: 412, 940: 679,
            941: 647, 942: None, 943: 333, 944: None, 945: 253, 946: None}

    pattern = """
def %(func)s():
    # origen
    origen = Categoria.objects.get(id=%(id)s)

    # destinos
    %(destinos_var)s

    mover(origen, intento_borrar=True,
          mapa=[%(mapa)s])
"""
    codigo = []
    funcs = []
    for cat in Categoria.por_clasificar():

        if cat.id in mapa and mapa[cat.id]:
            # el padre de la categoria que eligieron los usuarios
            probable_level2 = Categoria.objects.get(id=mapa[cat.id]).get_parent()
            params = {}
            func = slugify(cat.nombre).replace('-', '_')
            funcs.append(func)
            params['func'] = func
            params['id'] = cat.id
            (params['destinos_var'],
             params['mapa']) = _generar_codigo_de_destinos_para(probable_level2)
            codigo.append(pattern % params)
        else:
            print cat, cat.id
            print "   Defina un id probable de destino"

    main = "def main():\n" + "\n".join("    %s()" % s for s in funcs)
    codigo.append(main)
    return "\n".join(codigo)


def mover(origen, intento_borrar=False, log=True, mapa=[]):
    """
    mueve los productos de la categoria origen
    a las de destino, basadas en las claves
    de mapa.

    Ejemplo ::

        >>> # origen
            aceitunas = Categoria.objects.get(id=904)

            # destinos
            negras = Categoria.objects.get(id=232)
            verdes = Categoria.objects.get(id=234)
            mover(aceitunas, mapa=[('negras', negras), ('verdes', verdes)])

    Moverá todas los productos de ``aceitunas`` a ``verdes``
    las que tengan en su descripcion (campo ``busqueda``) la palabra
    clave ``verdes`` y a ``negras``  las que tengan la palabra clave
    ``negras``.

    Si ``intento_borrar`` es True, se elimina la categoria origen
    cuando no quedan productos.

    Si ``log`` es True imprime el movimiento
    """
    try:
        with transaction.atomic():
            for clave, destino in mapa.items():
                for p in origen.productos.filter(busqueda__icontains=clave):
                    p.categoria = destino
                    p.save(update_fields=['categoria'])
                    if log:
                        print p, "=>", destino

            if intento_borrar and origen.productos.count() == 0:
                print u"%s quedó vacia y se eliminará" % origen
                origen.delete()
    except Exception as e:
        print u"Hubo un error **no se migró nada**"
        print e.message


def aceites():
    # categoria origen
    aceites = Categoria.objects.get(id=937)

    # destinos
    girasol = Categoria.objects.get(id=228)
    oliva = Categoria.objects.get(id=231)
    maiz = Categoria.objects.get(id=229)

    mover(aceites, intento_borrar=True,
          mapa=[('girasol', girasol), ('oliva', oliva),
                ('maiz', maiz)])


def aceitunas():
    # origen
    aceitunas = Categoria.objects.get(id=904)

    # destinos
    negra = Categoria.objects.get(id=232)
    verde = Categoria.objects.get(id=234)
    rellena = Categoria.objects.get(id=233)
    encurtido = Categoria.objects.get(id=235)

    mover(aceitunas, intento_borrar=True,
          mapa=[('rellena', rellena), ('negra', negra),
                ('verde', verde), ('encurtido', encurtido)])

    # extra
    # mover
    # <Categoria: Fiambreria > Aceitunas/ encurtidos > Aceitunas/ encurtidos>
    aceituna_en_fiambreria = Categoria.objects.get(id=440)
    mover(aceituna_en_fiambreria, escabeche=encurtido)
    aceituna_en_fiambreria.get_parent().delete()


def vinagre_aceto():
    # origen
    origen = Categoria.objects.get(id=885)

    # destinos
    aceto = Categoria.objects.get(id=252)
    vinagre = Categoria.objects.get(id=261)

    mover(origen, intento_borrar=True,
          mapa=[('aceto', aceto), ('vinagre', vinagre)])


#
#  *********************************
#  todas las funciones de abajo son resultado de
#  metamagia()
#
#   con levels adaptaciones manuales.
#


