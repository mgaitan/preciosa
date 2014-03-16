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
    line = "%s = Categoria.objects.get(id=%d)   # %s"
    lines = []
    destinos = []
    for cat in cat_depth2.get_children():
        destino = cat.busqueda.split()[-1]
        if destino[-1] == 's':
            destino = destino[:-1]
        destinos.append(destino)
        lines.append(line % (destino, cat.id, cat.nombre))

    mapa = ", ".join("('%s', %s)" % (s, s) for s in destinos)
    return '\n    '.join(lines), mapa


def metamagia():
    """un intento de genera el codigo necesario para toda la zaraza
    de mudanzas"""

    # resultado de los voluntarios
    mapa = {773: 643, 774: 297, 775: 657, 776: 598,
            778: 282, 779: 706, 780: 226, 781: 628, 782: 661,
            783: 387, 784: 360, 785: 413, 786: 688, 787: 650,
            788: 287, 789: 637, 790: 600, 791: 702, 792: 612, 793: 589,
            794: 292, 795: 625, 796: 658, 797: 380, 798: 677, 799: 434,
            800: 634, 801: 413, 802: 360, 803: 654, 804: 459, 805: 682,
            806: 277, 807: 627, 808: 405, 809: 378, 810: 352, 811: 303,
            812: 550, 813: 391, 815: 284, 816: 657, 817: 303, 818: 384,
            819: 622, 820: 445, 821: 637, 822: 266, 824: 630,
            826: 666, 827: 416, 828: 613, 829: 362, 830: 316,
            831: 584, 832: 657, 833: 582, 834: 274, 835: 406, 836: 478,
            837: 292, 838: 289, 839: 351, 840: 291, 841: 296, 842: 697,
            844: 675, 845: 621, 846: 464, 847: 469, 848: 303,
            850: 294, 851: 643, 852: 651, 853: 521, 854: 291, 855: 626,
            857: 306, 858: 622, 860: 501, 861: 672, 862: 575,
            863: 298, 864: 352, 866: 428, 867: 292, 868: 643,
            869: 690, 870: 435, 871: 654, 872: 260, 873: 374, 874: 697,
            876: 456, 877: 314, 878: 359, 879: 606, 880: 293,
            881: 248, 882: 506, 884: 292, 885: 261, 886: 308,
            887: 270, 888: 661, 889: 292, 890: 579, 891: 678, 892: 472,
            893: 575, 894: 607, 895: 243, 897: 572,
            899: 576, 900: 404, 901: 601, 902: 390, 903: 643, 904: 234,
            905: 283, 906: 378, 907: 644, 908: 357, 909: 290, 910: 511,
            911: 290, 913: 593, 914: 676, 916: 315,
            917: 665, 918: 388, 919: 278, 920: 642, 921: 636, 922: 610,
            923: 374, 924: 599, 925: 304, 926: 635, 927: 629, 928: 374,
            929: 457, 930: 411, 931: 354, 932: 414, 933: 449, 934: 279,
            935: 356, 936: 444, 938: 591, 939: 412, 940: 679,
            941: 647, 943: 333, 945: 253,
            # definidos agregados manualmente
            814: 623, 859: 387, 849: 236, 898: 262, 896: 424,
            915: 466,   # complementar con 473
            875: 592, 912: 408, 883: 282, 942: 610, 946: 595,
            777: 512,
            865: 639,  # complementar con perros
            944: 950,  # corregir_nombres
            825: 453,
            843: 954,
            823: 958
            }
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
            probable_level2 = Categoria.objects.get(
                id=mapa[cat.id]).get_parent()
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


def mover(origen, intento_borrar=False, log=True, mapa=[], default=None):
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

    alternativamente, origen puede ser un queryset de productos

    Si ``intento_borrar`` es True, se elimina la categoria origen
    cuando no quedan productos.

    default es la categoria para todos los productos que no fueron
    movidos

    Si ``log`` es True imprime el movimiento
    """
    try:
        if isinstance(origen, Categoria):
            origen = origen.productos.all()
        else:
            # si no es categoria no se puede borrar.
            intento_borrar = False

        with transaction.atomic():
            for clave, destino in mapa:
                for p in origen.filter(busqueda__icontains=clave):
                    p.categoria = destino
                    p.save(update_fields=['categoria'])
                    if log:
                        print p, "=>", destino

            if default:
                for p in origen:
                    p.categoria = default
                    p.save(update_fields=['categoria'])
                    if log:
                        print p, "=>", default

            if intento_borrar and origen.count() == 0:
                print u"     ****  %s quedó vacia y se eliminará" % origen
                origen.delete()
    except Exception as e:
        print u"Hubo un error **no se migró nada**"
        print e.message


def aceites():
    # categoria origen
    return

    aceites = Categoria.objects.get(id=937)

    # destinos
    girasol = Categoria.objects.get(id=228)
    oliva = Categoria.objects.get(id=231)
    maiz = Categoria.objects.get(id=229)

    mover(aceites, intento_borrar=True, default=girasol,
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

    mover(aceitunas, intento_borrar=True, default=verde,
          mapa=[('rellena', rellena), ('negra', negra),
                ('verde', verde), ('encurtido', encurtido)])

    # extra
    # mover
    # <Categoria: Fiambreria > Aceitunas/ encurtidos > Aceitunas/ encurtidos>
    aceituna_en_fiambreria = Categoria.objects.get(id=440)
    mover(aceituna_en_fiambreria, default=encurtido)
    aceituna_en_fiambreria.get_parent().delete()


def vinagre_aceto():
    # origen
    return
    origen = Categoria.objects.get(id=885)

    # destinos
    aceto = Categoria.objects.get(id=252)
    vinagre = Categoria.objects.get(id=261)

    mover(origen, intento_borrar=True, default=vinagre,
          mapa=[('aceto', aceto)])


#
#  *********************************
#  todas las funciones de abajo son resultado de
#  metamagia()
#
#   con levels adaptaciones manuales.
#


def aceite_para_bebes():
    # origen
    origen = Categoria.objects.get(id=814)

    # destinos
    aceite = Categoria.objects.get(id=623)   # Aceites
    crema = Categoria.objects.get(id=624)   # Cremas

    mover(origen, intento_borrar=True,
          mapa=[('aceite', aceite), ('crema', crema)])


def acondicionador():
    # origen
    origen = Categoria.objects.get(id=888)

    # destinos
    # 1 = Categoria.objects.get(id=659)   # 2 en 1
    cabello = Categoria.objects.get(id=660)   # Accesorios cabello
    acondicionador = Categoria.objects.get(id=661)   # Acondicionador
    coloracion = Categoria.objects.get(id=662)   # Coloracion
    trat = Categoria.objects.get(id=663)   # Crema de peinar- trat
    fijacion = Categoria.objects.get(id=664)   # Gel y fijacion
    infantil = Categoria.objects.get(id=665)   # Infantil
    shampoo = Categoria.objects.get(id=666)   # Shampoo
    caida = Categoria.objects.get(id=667)   # Tratamiento control caida
    pediculosi = Categoria.objects.get(id=668)   # Tratamiento pediculosis
    caspa = Categoria.objects.get(id=669)   # Tratamientos anti caspa

    mover(origen, intento_borrar=True,
          mapa=[('cabello', cabello),
                ('acondicionador', acondicionador),
                ('coloracion', coloracion),
                ('trat', trat),
                ('fijacion', fijacion),
                ('infantil', infantil),
                ('shampoo', shampoo),
                ('caida', caida),
                ('pediculosi', pediculosi),
                ('caspa', caspa)], default=cabello)


def aderezos():
    # origen
    origen = Categoria.objects.get(id=872)

    # destinos
    aceto = Categoria.objects.get(id=252)   # Aceto
    especia = Categoria.objects.get(id=253)   # Especias
    limon = Categoria.objects.get(id=254)   # Jugo de limon
    mayonesa = Categoria.objects.get(id=255)   # Mayonesa
    mostaza = Categoria.objects.get(id=256)   # Mostaza
    saborizadore = Categoria.objects.get(id=257)   # Saborizadores
    sal = Categoria.objects.get(id=258)   # Sal
    ketchup = Categoria.objects.get(id=259)   # Salsa golf/ ketchup
    salsa = Categoria.objects.get(id=260)   # Salsas
    vinagre = Categoria.objects.get(id=261)   # Vinagre

    mover(origen, intento_borrar=True, default=salsa,
          mapa=[('aceto', aceto), ('especia', especia),
                ('limon', limon), ('mayonesa', mayonesa),
                ('mostaza', mostaza), ('saboriza', saborizadore),
                ('sal', sal), ('ketchup', ketchup),
                ('salsa', salsa),
                ('vinagre', vinagre)])


def afeitado():
    # origen
    origen = Categoria.objects.get(id=852)

    # destinos
    espuma = Categoria.objects.get(id=651)   # Cremas/ espumas
    filo = Categoria.objects.get(id=652)   # Filos
    shave = Categoria.objects.get(id=653)   # Locion/ after shave

    mover(origen, intento_borrar=True,
          mapa=[('crema', espuma), ('maquina', filo), ('cartucho', filo)])


def aguas():
    # origen
    origen = Categoria.objects.get(id=906)

    # destinos
    gasificada = Categoria.objects.get(id=377)   # Gasificadas
    saborizada = Categoria.objects.get(id=378)   # Saborizadas
    ga = Categoria.objects.get(id=379)   # Sin gas

    mover(origen, intento_borrar=True,
          mapa=[('gasificada', gasificada), ('saborizada', saborizada),
                ('sin ', ga)])


def aguas_saborizadas():
    # origen
    origen = Categoria.objects.get(id=809)

    # destinos
    gasificada = Categoria.objects.get(id=377)   # Gasificadas
    saborizada = Categoria.objects.get(id=378)   # Saborizadas
    ga = Categoria.objects.get(id=379)   # Sin gas

    mover(origen, intento_borrar=True,
          mapa=[('gasificada', gasificada), ('saborizada', saborizada), ('ga', ga)])


def ahumados():
    # origen
    origen = Categoria.objects.get(id=820)

    # destinos
    ahumado = Categoria.objects.get(id=445)   # Ahumados
    especiale = Categoria.objects.get(id=446)   # Especiales
    cocido = Categoria.objects.get(id=447)   # Jamon cocido
    bondiola = Categoria.objects.get(id=448)   # Jamon crudo/ bondiola
    salchichon = Categoria.objects.get(id=449)   # Mortadela/ salchichon
    pate = Categoria.objects.get(id=450)   # Pate
    salamine = Categoria.objects.get(id=451)   # Salame y salamines

    mover(origen, intento_borrar=True,
          mapa=[('ahumado', ahumado),
                ('especial', especiale),
                ('cocido', cocido),
                ('bondiola', bondiola),
                ('salchichon', salchichon),
                ('pate', pate),
                ('salamin', salamine)])


def algodon():
    # origen
    origen = Categoria.objects.get(id=803)

    # destinos
    hisopo = Categoria.objects.get(id=654)   # Algodon/ hisopos

    mover(origen, intento_borrar=True,
          mapa=[('hisopo', hisopo)])


def amargos():
    # origen
    origen = Categoria.objects.get(id=859)

    # destinos
    hierba = Categoria.objects.get(id=859)   # Amargos / Hierbas

    mover(origen, intento_borrar=True, default=hierba)


def aperitivos():
    # origen
    origen = Categoria.objects.get(id=839)

    # destinos
    americano = Categoria.objects.get(id=349)   # Americano
    fernet = Categoria.objects.get(id=350)   # Fernet
    vermouth = Categoria.objects.get(id=351)   # Vermouth

    mover(origen, intento_borrar=True, default=vermouth,
          mapa=[('americano', americano), ('fernet', fernet), ('verm', vermouth)])


def arroz():
    # origen
    origen = Categoria.objects.get(id=849)

    # destinos
    doble = Categoria.objects.get(id=236)   # Doble
    especiale = Categoria.objects.get(id=237)   # Especiales
    largo = Categoria.objects.get(id=238)   # Grano largo
    integral = Categoria.objects.get(id=239)   # Integral
    parboil = Categoria.objects.get(id=240)   # Parboil
    preparado = Categoria.objects.get(id=241)   # Preparados

    mover(origen, intento_borrar=True, default=largo,
          mapa=[('doble', doble), ('especiale', especiale),
                ('parboil', parboil),
                ('preparado', preparado), ('list', preparado),
                ('largo', largo),
                ('integral', integral)])


def azucar_y_endulzantes():
    # origen
    origen = Categoria.objects.get(id=895)

    # destinos
    azucar = Categoria.objects.get(id=242)   # Azucar
    edulcorante = Categoria.objects.get(id=243)   # Edulcorante

    mover(origen, intento_borrar=True,
          mapa=[('azucar', azucar), ('edulcorante', edulcorante)])


def bazar():
    # origen
    origen = Categoria.objects.get(id=943)

    # destinos
    copa = Categoria.objects.get(id=332)   # Copas
    vaso = Categoria.objects.get(id=333)   # Vasos

    mover(origen, intento_borrar=True,
          mapa=[('copa', copa), ('vaso', vaso)])


def bebidas_blancas():
    # origen
    origen = Categoria.objects.get(id=864)

    # destinos
    blanca = Categoria.objects.get(id=352)   # Blancas

    mover(origen, intento_borrar=True,
          mapa=[('blanca', blanca)])


def bebidas_energizantes():
    # origen
    origen = Categoria.objects.get(id=797)

    # destinos
    energizante = Categoria.objects.get(id=380)   # Energizantes

    mover(origen, intento_borrar=True,
          mapa=[('energizante', energizante)])


def bebidas_fizz():
    # origen
    origen = Categoria.objects.get(id=784)

    # destinos
    otro = Categoria.objects.get(id=360)   # Sidras- otros

    mover(origen, intento_borrar=True,
          mapa=[('otro', otro)])


def bebidas_isotonicas():
    # origen
    origen = Categoria.objects.get(id=918)

    # destinos
    isotonica = Categoria.objects.get(id=388)   # Isotonicas

    mover(origen, intento_borrar=True,
          mapa=[('isotonica', isotonica)])


def bizcochos():
    # origen
    origen = Categoria.objects.get(id=846)

    # destinos
    bizcocho = Categoria.objects.get(id=464)   # Bizcochos

    mover(origen, intento_borrar=True,
          mapa=[('bizcocho', bizcocho)])


def bocaditos():
    # origen
    origen = Categoria.objects.get(id=801)

    # destinos
    pescado = Categoria.objects.get(id=412)   # Pescado
    pollo = Categoria.objects.get(id=413)   # Pollo
    soja = Categoria.objects.get(id=414)   # Soja
    verdura = Categoria.objects.get(id=415)   # Verdura

    mover(origen, intento_borrar=True,
          mapa=[('pescado', pescado),
                ('pollo', pollo),
                ('soja', soja),
                ('verdura', verdura)])


def bolsas_para_residuos():
    # origen
    origen = Categoria.objects.get(id=893)

    # destinos
    freezer = Categoria.objects.get(id=573)   # Bolsa freezer
    reutilizable = Categoria.objects.get(id=574)   # Bolsa reutilizable
    descartable = Categoria.objects.get(id=575)   # Descartables
    lavavajilla = Categoria.objects.get(id=576)   # Detergente- lavavajilla
    papele = Categoria.objects.get(id=577)   # Films- papeles
    encendedore = Categoria.objects.get(id=578)   # Fosforos / encendedores
    # Limpiadores- desengrasantes
    desengrasante = Categoria.objects.get(id=579)
    palillero = Categoria.objects.get(id=580)   # Palillero
    palillo = Categoria.objects.get(id=581)   # Palillos
    vela = Categoria.objects.get(id=582)   # Velas

    mover(origen, intento_borrar=True,
          mapa=[('freezer', freezer),
                ('reutilizable', reutilizable),
                ('descartable', descartable),
                ('lavavajilla', lavavajilla),
                ('papel', papele),
                ('encendedor', encendedore),
                ('desengrasante', desengrasante),
                ('palillero', palillero),
                ('palillo', palillo), ('vela', vela)])


def brownies_y_budines():
    # origen
    origen = Categoria.objects.get(id=911)

    # destinos
    budines = Categoria.objects.get(id=290)   # Budines/otros

    mover(origen, intento_borrar=True, default=budines)


def cacao_en_polvo():
    # origen
    origen = Categoria.objects.get(id=919)

    # destinos
    cacao = Categoria.objects.get(id=278)   # Cacao
    mover(origen, intento_borrar=True, default=cacao)


def cafe():
    # origen
    origen = Categoria.objects.get(id=934)

    # destinos
    instantaneo = Categoria.objects.get(id=279)   # Cafe instantaneo
    torrado = Categoria.objects.get(id=280)   # Cafe p/ filtro
    filtro = Categoria.objects.get(id=281)   # Filtro cafe
    malta = Categoria.objects.get(id=961)   # Maltas

    mover(origen, intento_borrar=True, default=torrado,
          mapa=[('instantaneo', instantaneo),
                ('filtro', filtro),
                ('torrado', cafe),
                ('tostado', cafe),
                ('malta', malta)])


def caldos_y_saborizadores():
    # origen
    origen = Categoria.objects.get(id=877)

    # destinos
    caldo = Categoria.objects.get(id=313)   # Caldos
    saborizadore = Categoria.objects.get(id=314)   # Saborizadores
    sopa = Categoria.objects.get(id=315)   # Sopas

    mover(origen, intento_borrar=True,
          mapa=[('caldo', caldo), ('saborizadore', saborizadore), ('sopa', sopa)])


def cepillos_dentales():
    # origen
    origen = Categoria.objects.get(id=914)

    # destinos

    cepillo = Categoria.objects.get(id=676)   # Cepillos

    mover(origen, intento_borrar=True, default=cepillo)


def cereales():
    # origen
    origen = Categoria.objects.get(id=881)

    # destinos
    avena = Categoria.objects.get(id=244)   # Avena
    azucarado = Categoria.objects.get(id=245)   # Azucarados
    barra = Categoria.objects.get(id=246)   # Barras
    chocolate = Categoria.objects.get(id=247)   # Chocolate
    frutal = Categoria.objects.get(id=248)   # Frutal
    maiz = Categoria.objects.get(id=249)   # Maiz
    miel = Categoria.objects.get(id=250)   # Miel
    multicereal = Categoria.objects.get(id=251)   # Multicereal

    mover(origen, intento_borrar=True, default=multicereal,
          mapa=[('avena', avena), ('azucarado', azucarado),
                ('barra', barra), ('chocolate', chocolate),
                ('fruta', frutal), ('maiz', maiz),
                ('miel', miel), ('multicereal', multicereal)])


def cervezas():
    # origen
    origen = Categoria.objects.get(id=931)

    # destinos
    artesanal = Categoria.objects.get(id=353)   # Artesanal
    botella = Categoria.objects.get(id=354)   # Botella
    lata = Categoria.objects.get(id=355)   # Lata

    mover(origen, intento_borrar=True,
          mapa=[('artesanal', artesanal), ('botella', botella), ('lata', lata)])


def chocolates():
    # origen
    origen = Categoria.objects.get(id=836)
    # destinos
    tablet = Categoria.objects.get(id=478)   # Chocolates y tablet
    mover(origen, intento_borrar=True, default=tablet)


def coberturas():
    # origen
    origen = Categoria.objects.get(id=857)

    # destinos
    bizcochuelo = Categoria.objects.get(id=305)   # Bizcochuelos
    reposteria = Categoria.objects.get(id=306)   # Reposteria

    mover(origen, intento_borrar=True,
          mapa=[('bizcochuelo', bizcochuelo), ('reposteria', reposteria)])


def cocina():
    # origen
    origen = Categoria.objects.get(id=899)

    # destinos
    freezer = Categoria.objects.get(id=573)   # Bolsa freezer
    reutilizable = Categoria.objects.get(id=574)   # Bolsa reutilizable
    descartable = Categoria.objects.get(id=575)   # Descartables
    lavavajilla = Categoria.objects.get(id=576)   # Detergente- lavavajilla
    papele = Categoria.objects.get(id=577)   # Films- papeles
    encendedore = Categoria.objects.get(id=578)   # Fosforos / encendedores
    # Limpiadores- desengrasantes
    desengrasante = Categoria.objects.get(id=579)
    palillero = Categoria.objects.get(id=580)   # Palillero
    palillo = Categoria.objects.get(id=581)   # Palillos
    vela = Categoria.objects.get(id=582)   # Velas

    mover(origen, intento_borrar=True, default=descartable,
          mapa=[('freezer', freezer),
                ('reutilizable', reutilizable),
                ('descartable', descartable),
                ('lavavajilla', lavavajilla),
                ('papele', papele),
                ('encendedore', encendedore),
                ('desengrasante', desengrasante),
                ('palillero', palillero), ('palillo', palillo),
                ('vela', vela)])


def colonia_para_bebes():
    # origen
    origen = Categoria.objects.get(id=927)

    # destinos
    nino = Categoria.objects.get(id=629)   # Bebes/ niños

    mover(origen, intento_borrar=True, default=nino)


def colonias_y_perfumes():
    # origen
    origen = Categoria.objects.get(id=869)

    # destinos
    nino = Categoria.objects.get(id=691)   # Bebes/ niños
    splash = Categoria.objects.get(id=692)   # Body splash
    hombre = Categoria.objects.get(id=693)   # Hombre
    mujer = Categoria.objects.get(id=694)   # Mujer

    mover(origen, intento_borrar=True, default=mujer,
          mapa=[('nino', nino), ('bebe', nino), ('splash', splash),
                ('hombre', hombre),
                ('women', hombre),
                ('men', hombre),
                ('mujer', mujer)])


def comidas_preparadas():
    # origen
    origen = Categoria.objects.get(id=868)

    # destinos
    vario = Categoria.objects.get(id=643)   # Varios

    mover(origen, intento_borrar=True, default=vario)


def comidas_para_bebes():
    # origen
    origen = Categoria.objects.get(id=855)

    # destinos
    alimento = Categoria.objects.get(id=625)   # Leche - alimento
    papilla = Categoria.objects.get(id=626)   # Papilla

    mover(origen, intento_borrar=True,
          mapa=[('alimento', alimento), ('papilla', papilla)])


def condimentos_y_especias():
    # origen
    origen = Categoria.objects.get(id=945)

    # destinos

    especia = Categoria.objects.get(id=253)   # Especias
    saborizadore = Categoria.objects.get(id=257)   # Saborizadores

    mover(origen, intento_borrar=True, default=especia,
          mapa=[('saboriza', saborizadore), ('caldo', saborizadore)])


def conservas():
    # origen
    origen = Categoria.objects.get(id=898)

    # destinos
    carne = Categoria.objects.get(id=262)   # Carnes
    fruta = Categoria.objects.get(id=263)   # Frutas
    pescado = Categoria.objects.get(id=264)   # Pescados
    salsa = Categoria.objects.get(id=265)   # Tomates/ salsas
    vegetale = Categoria.objects.get(id=266)   # Vegetales

    mover(origen, intento_borrar=True, default=vegetale,
          mapa=[('carne', carne), ('fruta', fruta), ('pescado', pescado),
                ('salsa', salsa), ('vegetale', vegetale)])


def cremas():
    # origen
    origen = Categoria.objects.get(id=860)

    # destinos
    crema = Categoria.objects.get(id=501)   # Cremas

    mover(origen, intento_borrar=True, default=crema)


def cremas_corporales():
    # origen
    origen = Categoria.objects.get(id=775)

    # destinos
    splash = Categoria.objects.get(id=655)   # Body splash
    bronceadore = Categoria.objects.get(id=656)   # Bronceadores
    crema = Categoria.objects.get(id=657)   # Cremas
    depilacion = Categoria.objects.get(id=658)   # Depilacion

    mover(origen, intento_borrar=True, default=crema,
          mapa=[('splash', splash), ('bronceador', bronceadore),
                ('crema', crema), ('depilacion', depilacion)])


def cremas_dentales():
    # origen
    origen = Categoria.objects.get(id=798)

    # destinos
    adhesivo = Categoria.objects.get(id=675)   # Adhesivos
    cepillo = Categoria.objects.get(id=676)   # Cepillos
    crema = Categoria.objects.get(id=677)   # Cremas
    enjuague = Categoria.objects.get(id=678)   # Enjuagues
    hilo = Categoria.objects.get(id=679)   # Hilo

    mover(origen, intento_borrar=True, default=crema,
          mapa=[('adhesivo', adhesivo), ('cepillo', cepillo),
                ('dentifrico', crema), ('crema', crema),
                ('enjuague', enjuague), ('hilo', hilo)])


def cremas_faciales():
    # origen
    origen = Categoria.objects.get(id=861)

    # destinos
    antiacne = Categoria.objects.get(id=670)   # Antiacne
    antiarruga = Categoria.objects.get(id=671)   # Antiarrugas
    hidratacion = Categoria.objects.get(id=672)   # Hidratacion
    cuti = Categoria.objects.get(id=673)   # Limpieza cutis
    esponja = Categoria.objects.get(id=674)   # Pinceles y esponjas

    mover(origen, intento_borrar=True, default=hidratacion,
          mapa=[('acne', antiacne), ('antiarruga', antiarruga),
                ('hidratacion', hidratacion), ('cuti', cuti), ('esponja', esponja)])


def cuidado_de_la_piel():
    # origen
    origen = Categoria.objects.get(id=816)

    # destinos
    splash = Categoria.objects.get(id=655)   # Body splash
    bronceadore = Categoria.objects.get(id=656)   # Bronceadores
    crema = Categoria.objects.get(id=657)   # Cremas
    depilacion = Categoria.objects.get(id=658)   # Depilacion

    mover(origen, intento_borrar=True, default=crema,
          mapa=[('splash', splash), ('bronceadore', bronceadore),
                ('crema', crema), ('depilacion', depilacion)])


def cuidado_del_cabello():
    # origen
    origen = Categoria.objects.get(id=782)

    # destinos
    cabello = Categoria.objects.get(id=660)   # Accesorios cabello
    acondicionador = Categoria.objects.get(id=661)   # Acondicionador
    coloracion = Categoria.objects.get(id=662)   # Coloracion
    trat = Categoria.objects.get(id=663)   # Crema de peinar- trat
    fijacion = Categoria.objects.get(id=664)   # Gel y fijacion
    infantil = Categoria.objects.get(id=665)   # Infantil
    shampoo = Categoria.objects.get(id=666)   # Shampoo
    caida = Categoria.objects.get(id=667)   # Tratamiento control caida
    pediculosi = Categoria.objects.get(id=668)   # Tratamiento pediculosis
    caspa = Categoria.objects.get(id=669)   # Tratamientos anti caspa

    mover(origen, intento_borrar=True, default=trat,
          mapa=[('accesorio', cabello),
                ('acondicionador', acondicionador),
                ('coloracion', coloracion),
                ('trat', trat), ('fijacion', fijacion),
                ('infantil', infantil), ('shampoo', shampoo),
                ('caida', caida), ('pediculosi', pediculosi),
                ('caspa', caspa)])


def depilacion():
    # origen
    origen = Categoria.objects.get(id=796)

    depilacion = Categoria.objects.get(id=658)   # Depilacion

    mover(origen, intento_borrar=True, default=depilacion)


def desodorantes():
    # origen
    origen = Categoria.objects.get(id=805)

    # destinos
    hombre = Categoria.objects.get(id=680)   # Hombre
    infantil = Categoria.objects.get(id=681)   # Infantil
    mujer = Categoria.objects.get(id=682)   # Mujer

    mover(origen, intento_borrar=True,
          mapa=[('hombre', hombre), ('infantil', infantil),
                ('mujer', mujer), ('nino', infantil), ('axe', hombre)])


def desodorantes_de_ambientes():
    # origen
    origen = Categoria.objects.get(id=831)

    # destinos
    aerosole = Categoria.objects.get(id=584)   # Aerosoles
    antihumedad = Categoria.objects.get(id=585)   # Antihumedad
    aromatizadore = Categoria.objects.get(id=586)   # Aromatizadores
    atomizador = Categoria.objects.get(id=587)   # Atomizador

    mover(origen, intento_borrar=True, default=aerosole,
          mapa=[('aromatizador', aromatizadore), ('atomizador', atomizador),
                ('aerosol', aerosole), ('antihumedad', antihumedad)])


def destapacanerias():
    # origen
    origen = Categoria.objects.get(id=858)

    # destinos
    vario = Categoria.objects.get(id=622)   # Varios

    mover(origen, intento_borrar=True, default=vario)


def dulces():
    # origen
    origen = Categoria.objects.get(id=887)

    # destinos
    light = Categoria.objects.get(id=267)   # Diet- light
    leche = Categoria.objects.get(id=268)   # Dulce de leche
    jalea = Categoria.objects.get(id=269)   # Jalea
    mermelada = Categoria.objects.get(id=270)   # Mermelada
    otro = Categoria.objects.get(id=271)   # Miel- otros

    mover(origen, intento_borrar=True, default=otro,
          mapa=[('light', light), ('leche', leche),
                ('jalea', jalea), ('mermelada', mermelada), ('otro', otro)])


def emulsiones_limpiadoras_para_bebes():
    # origen
    origen = Categoria.objects.get(id=824)

    # destinos
    calcareo = Categoria.objects.get(id=630)   # Oleo calcareo

    mover(origen, intento_borrar=True, default=calcareo)


def enjuagues_bucales():
    # origen
    origen = Categoria.objects.get(id=891)

    # destinos
    enjuague = Categoria.objects.get(id=678)   # Enjuagues
    mover(origen, intento_borrar=True, default=enjuague)


def escobas_escobillones_y_cepillos():
    # origen
    origen = Categoria.objects.get(id=793)

    # destinos
    cabo = Categoria.objects.get(id=588)   # Cabos
    cepillo = Categoria.objects.get(id=589)   # Escobas- cepillos
    escobillone = Categoria.objects.get(id=590)   # Escobillones

    mover(origen, intento_borrar=True, default=escobillone,
          mapa=[('cabo', cabo), ('palo', cabo),
                ('cepillo', cepillo), ('escobillon', escobillone)])


def esponjas():
    # origen
    origen = Categoria.objects.get(id=938)

    # destinos
    esponja = Categoria.objects.get(id=591)   # Esponjas

    mover(origen, intento_borrar=True, default=esponja)


def farmacia():
    # origen
    origen = Categoria.objects.get(id=896)

    # destinos
    oxigenada = Categoria.objects.get(id=424)   # Agua oxigenada
    alcohol = Categoria.objects.get(id=425)   # Alcohol
    venda = Categoria.objects.get(id=426)   # Gasas- vendas
    botiquin = Categoria.objects.get(id=427)   # Otros botiquin

    mover(origen, intento_borrar=True, default=botiquin,
          mapa=[('oxigenada', oxigenada), ('alcohol', alcohol),
                ('venda', venda), ('botiquin', botiquin)])


def fiambres_y_embutidos():
    # origen
    origen = Categoria.objects.get(id=933)

    # destinos
    ahumado = Categoria.objects.get(id=445)   # Ahumados
    especiale = Categoria.objects.get(id=446)   # Especiales
    cocido = Categoria.objects.get(id=447)   # Jamon cocido
    bondiola = Categoria.objects.get(id=448)   # Jamon crudo/ bondiola
    salchichon = Categoria.objects.get(id=449)   # Mortadela/ salchichon
    pate = Categoria.objects.get(id=450)   # Pate
    salamine = Categoria.objects.get(id=451)   # Salame y salamines

    mover(origen, intento_borrar=True, default=especiale,
          mapa=[('ahumado', ahumado), ('cocido', cocido),
                ('bondiola', bondiola), ('salchichon', salchichon),
                ('pate', pate), ('salamine', salamine)])


def frutas():
    # origen
    origen = Categoria.objects.get(id=804)

    # destinos
    fruta = Categoria.objects.get(id=459)   # Frutas

    mover(origen, intento_borrar=True, default=fruta)


def galletas_y_galletitas():
    # origen
    origen = Categoria.objects.get(id=915)

    # destinos
    chocolate = Categoria.objects.get(id=466)   # Chocolate
    hojaldre = Categoria.objects.get(id=467)   # Hojaldre
    madalena = Categoria.objects.get(id=468)   # Madalenas
    rellena = Categoria.objects.get(id=469)   # Rellenas
    seca = Categoria.objects.get(id=470)   # Secas
    cereal = Categoria.objects.get(id=471)  # Cereal
    marineras = Categoria.objects.get(id=472)  # Grisines- marineras
    regulares = Categoria.objects.get(id=473)  # Regulares
    snacks = Categoria.objects.get(id=474)  # Snacks

    mover(origen, intento_borrar=True, default=regulares,
          mapa=[('chocolate', chocolate), ('cereal', cereal),
                ('marinera', marineras), ('cracker', regulares),
                ('snack', snacks), ('rellena', rellena),
                ('hojaldre', hojaldre), ('madalena', madalena),
                ('seca', seca)])


def gaseosas():
    # origen
    origen = Categoria.objects.get(id=818)

    # destinos
    cola = Categoria.objects.get(id=381)   # Cola
    limon = Categoria.objects.get(id=382)   # Lima limon
    naranja = Categoria.objects.get(id=383)   # Naranja
    otra = Categoria.objects.get(id=384)   # Otras
    pomelo = Categoria.objects.get(id=385)   # Pomelo
    tonica = Categoria.objects.get(id=386)   # Tonica

    mover(origen, intento_borrar=True,
          mapa=[('cola', cola), ('limon', limon), ('naranja', naranja),
                ('otra', otra), ('pomelo', pomelo), ('tonica', tonica)])


def gel_de_ducha():
    # origen
    origen = Categoria.objects.get(id=874)

    # destinos
    liquido = Categoria.objects.get(id=697)   # Liquidos
    mover(origen, intento_borrar=True, default=liquido)


def grisines():
    # origen
    origen = Categoria.objects.get(id=892)

    # destinos
    marinera = Categoria.objects.get(id=472)   # Grisines- marineras

    mover(origen, intento_borrar=True, default=marinera)


def guantes_multiuso():
    # origen
    origen = Categoria.objects.get(id=875)

    # destinos
    guante = Categoria.objects.get(id=592)   # Guantes

    mover(origen, intento_borrar=True, default=guante)


def hamburguesas():
    # origen
    origen = Categoria.objects.get(id=835)

    # destinos
    carne = Categoria.objects.get(id=406)   # Carne
    soja = Categoria.objects.get(id=407)   # Soja

    mover(origen, intento_borrar=True, default=carne,
          mapa=[('carne', carne), ('soja', soja)])


def harinas():
    # origen
    origen = Categoria.objects.get(id=834)

    # destinos
    maiz = Categoria.objects.get(id=273)   # Maiz
    premezcla = Categoria.objects.get(id=274)   # Premezcla
    otra = Categoria.objects.get(id=275)   # Semola- otras
    trigo = Categoria.objects.get(id=276)   # Trigo

    mover(origen, intento_borrar=True, default=trigo,
          mapa=[('maiz', maiz), ('premezcla', premezcla),
                ('otra', otra), ('trigo', trigo)])


def helados_y_postres():
    # origen
    origen = Categoria.objects.get(id=912)

    # destinos
    palito = Categoria.objects.get(id=408)   # Palito
    postre = Categoria.objects.get(id=409)   # Postres
    balde = Categoria.objects.get(id=410)   # Potes y baldes

    mover(origen, intento_borrar=True, default=postre,
          mapa=[('palito', palito), ('postre', postre), ('balde', balde)])


def hilo_dental():
    # origen
    origen = Categoria.objects.get(id=940)

    # destinos
    hilo = Categoria.objects.get(id=679)   # Hilo

    mover(origen, intento_borrar=True, default=hilo)


def hisopos():
    # origen
    origen = Categoria.objects.get(id=871)

    # destinos
    hisopo = Categoria.objects.get(id=654)   # Algodon/ hisopos

    mover(origen, intento_borrar=True, default=hisopo)


def huevos():
    # origen
    origen = Categoria.objects.get(id=806)

    # destinos
    huevo = Categoria.objects.get(id=277)   # Huevos

    mover(origen, intento_borrar=True, default=huevo)


def infusiones():
    # origen
    origen = Categoria.objects.get(id=883)

    # destinos
    cacao = Categoria.objects.get(id=278)   # Cacao
    instantaneo = Categoria.objects.get(id=279)   # Cafe instantaneo
    filtro = Categoria.objects.get(id=280)   # Cafe p/ filtro
    cafe = Categoria.objects.get(id=281)   # Filtro cafe
    malta = Categoria.objects.get(id=961)   # Maltas
    cocido = Categoria.objects.get(id=282)   # Mate cocido
    te = Categoria.objects.get(id=283)   # Te
    yerba = Categoria.objects.get(id=284)   # Yerba

    mover(origen, intento_borrar=True, default=te,
          mapa=[('cacao', cacao), ('instantaneo', instantaneo),
                ('filtro', filtro), ('cafe', cafe), ('malta', malta),
                ('cocido', cocido), ('yerba', yerba), ('te', te)])


def insecticidas_y_repelentes():
    # origen
    origen = Categoria.objects.get(id=913)

    # destinos
    cucaracha = Categoria.objects.get(id=593)   # Cucarachas
    hormiga = Categoria.objects.get(id=594)   # Hormigas
    mosquito = Categoria.objects.get(id=595)   # Moscas y mosquitos
    pulga = Categoria.objects.get(id=596)   # Polillas y pulgas
    repelente = Categoria.objects.get(id=597)   # Repelentes

    mover(origen, intento_borrar=True, default=mosquito,
          mapa=[('cucaracha', cucaracha), ('hormiga', hormiga),
                ('mosquito', mosquito), ('pulga', pulga), ('repelente', repelente)])


def jabones_y_banos_liquidos():
    # origen
    origen = Categoria.objects.get(id=842)

    # destinos
    antiseptico = Categoria.objects.get(id=695)   # Antiseptico
    glicerina = Categoria.objects.get(id=696)   # Glicerina
    liquido = Categoria.objects.get(id=697)   # Liquidos
    tocador = Categoria.objects.get(id=698)   # Tocador

    mover(origen, intento_borrar=True, default=tocador,
          mapa=[('antiseptico', antiseptico),
                ('glicerina', glicerina), ('liquido', liquido), ('tocador', tocador)])


def jabones_y_banos_liquidos_para_bebes():
    # origen
    origen = Categoria.objects.get(id=917)

    dest = Categoria.objects.get(id=950)
    mover(origen, intento_borrar=True, default=dest)


def jugos():
    # origen
    origen = Categoria.objects.get(id=813)

    # destinos
    concentrado = Categoria.objects.get(id=389)   # Concentrados
    polvo = Categoria.objects.get(id=390)   # En polvo
    listo = Categoria.objects.get(id=391)   # Listos
    soja = Categoria.objects.get(id=392)   # Soja

    mover(origen, intento_borrar=True, default=listo,
          mapa=[('concentrado', concentrado), ('polvo', polvo),
                ('listo', listo), ('soja', soja)])


def jugos_en_polvo():
    # origen
    origen = Categoria.objects.get(id=902)

    # destinos
    polvo = Categoria.objects.get(id=390)   # En polvo

    mover(origen, intento_borrar=True, default=polvo)


def lavandinas():
    # origen
    origen = Categoria.objects.get(id=790)

    # destinos
    lavandina = Categoria.objects.get(id=583)   # lavandinas

    bano = Categoria.objects.get(id=598)   # Baño
    cocina = Categoria.objects.get(id=599)   # Cocina
    piso = Categoria.objects.get(id=600)   # Pisos
    mueble = Categoria.objects.get(id=601)   # Placard- muebles
    multiuso = Categoria.objects.get(id=602)   # Vidrios- multiuso

    mover(origen, intento_borrar=True, default=lavandina,
          mapa=[('bano', bano), ('cocina', cocina), ('piso', piso),
                ('mueble', mueble), ('multiuso', multiuso)])


def leche():
    # origen
    origen = Categoria.objects.get(id=882)

    # destinos
    chocolatada = Categoria.objects.get(id=505)   # Chocolatada
    descremada = Categoria.objects.get(id=506)   # Descremada
    entera = Categoria.objects.get(id=507)   # Entera
    infantil = Categoria.objects.get(id=508)   # Infantil
    polvo = Categoria.objects.get(id=509)   # Polvo
    saborizada = Categoria.objects.get(id=510)   # Saborizadas

    mover(origen, intento_borrar=True, default=entera,
          mapa=[('chocolatada', chocolatada),
                ('descremada', descremada), ('entera', entera),
                ('infantil', infantil), ('polvo', polvo),
                ('saborizada', saborizada)])


def leche_en_polvo():
    # origen
    origen = Categoria.objects.get(id=788)

    # destinos
    condensada = Categoria.objects.get(id=285)   # Condensada
    descremada = Categoria.objects.get(id=286)   # Descremada
    entera = Categoria.objects.get(id=287)   # Entera

    mover(origen, intento_borrar=True, default=entera,
          mapa=[('condensada', condensada),
                ('descremada', descremada), ('entera', entera)])


def leche_y_formulas_para_bebes():
    # origen
    origen = Categoria.objects.get(id=795)

    # destinos
    alimento = Categoria.objects.get(id=625)   # Leche - alimento
    papilla = Categoria.objects.get(id=626)   # Papilla

    mover(origen, intento_borrar=True, default=alimento,
          mapa=[('alimento', alimento), ('papilla', papilla), ('nestum', papilla)])


def levaduras():
    # origen
    origen = Categoria.objects.get(id=910)

    # destinos
    grasa = Categoria.objects.get(id=511)   # Levaduras y grasas

    mover(origen, intento_borrar=True, default=grasa)


def libreria_y_oficinas():
    # origen
    origen = Categoria.objects.get(id=812)

    # destinos
    accesorio = Categoria.objects.get(id=549)   # Accesorios
    dispensore = Categoria.objects.get(id=550)   # Cintas/ dispensores
    clips = Categoria.objects.get(id=551)   # Clips-alfileres-aros
    ojalillo = Categoria.objects.get(id=552)   # Etiquetas- ojalillos
    autoadhesiva = Categoria.objects.get(id=553)   # Notas autoadhesivas
    resma = Categoria.objects.get(id=554)   # Resmas

    mover(origen, intento_borrar=True, default=accesorio,
          mapa=[('accesorio', accesorio),
                ('dispensore', dispensore),
                ('clips',
                 clips),
                ('alfiler',
                 clips),
                ('aros',
                 clips),
                ('ojalillo', ojalillo),
                ('autoadhesiva', autoadhesiva),
                ('resma', resma), ('papel', resma)])


def licores():
    # origen
    origen = Categoria.objects.get(id=878)

    # destinos
    licore = Categoria.objects.get(id=359)   # Licores

    mover(origen, intento_borrar=True, default=licore)


def limpiador_de_vidrios_y_multiusos():
    # origen
    origen = Categoria.objects.get(id=890)

    # destinos

    mover(origen, intento_borrar=True, default=Categoria.objects.get(id=602))


def limpieza_facial():
    # origen
    origen = Categoria.objects.get(id=832)

    # destinos
    antiacne = Categoria.objects.get(id=670)   # Antiacne
    antiarruga = Categoria.objects.get(id=671)   # Antiarrugas
    hidratacion = Categoria.objects.get(id=672)   # Hidratacion
    cuti = Categoria.objects.get(id=673)   # Limpieza cutis
    esponja = Categoria.objects.get(id=674)   # Pinceles y esponjas

    mover(origen, intento_borrar=True, default=cuti,
          mapa=[('acne', antiacne), ('antiarruga', antiarruga),
                ('hidratacion', hidratacion), ('cuti', cuti), ('esponja', esponja)])


def limpieza_de_pisos():
    # origen
    origen = Categoria.objects.get(id=942)

    # destinos
    limpiadore = Categoria.objects.get(id=610)   # Limpiadores
    secadore = Categoria.objects.get(id=611)   # Secadores
    mopa = Categoria.objects.get(id=612)   # Trapos- mopas

    mover(origen, intento_borrar=True, default=limpiadore,
          mapa=[('limpiador', limpiadore), ('secadore', secadore),
                ('mopa', mopa), ('trapo', mopa)])


def limpieza_de_la_cocina():
    # origen
    origen = Categoria.objects.get(id=862)

    # destinos
    freezer = Categoria.objects.get(id=573)   # Bolsa freezer
    reutilizable = Categoria.objects.get(id=574)   # Bolsa reutilizable
    descartable = Categoria.objects.get(id=575)   # Descartables
    lavavajilla = Categoria.objects.get(id=576)   # Detergente- lavavajilla
    papele = Categoria.objects.get(id=577)   # Films- papeles
    encendedore = Categoria.objects.get(id=578)   # Fosforos / encendedores
    # Limpiadores- desengrasantes
    desengrasante = Categoria.objects.get(id=579)
    palillero = Categoria.objects.get(id=580)   # Palillero
    palillo = Categoria.objects.get(id=581)   # Palillos
    vela = Categoria.objects.get(id=582)   # Velas

    mover(origen, intento_borrar=True, default=desengrasante,
          mapa=[('freezer', freezer),
                ('reutilizable', reutilizable),
                ('descartable', descartable), ('detergente', lavavajilla),
                ('lavavajilla', lavavajilla), ('papele', papele),
                ('encendedor', encendedore), ('desengrasante', desengrasante),
                ('palillero', palillero), ('palillo', palillo), ('vela', vela)])


def limpieza_de_la_ropa():
    # origen
    origen = Categoria.objects.get(id=845)

    # destinos
    apresto = Categoria.objects.get(id=614)   # Aprestos
    blanqueador = Categoria.objects.get(id=615)   # Blanqueador
    fina = Categoria.objects.get(id=616)   # Fina
    jabon = Categoria.objects.get(id=617)   # Jabon
    perfume = Categoria.objects.get(id=618)   # Perfume
    quitamancha = Categoria.objects.get(id=619)   # Quitamanchas
    color = Categoria.objects.get(id=620)   # Reavivador de color
    suavizante = Categoria.objects.get(id=621)   # Suavizante

    mover(origen, intento_borrar=True, default=jabon,
          mapa=[('apresto', apresto),
                ('blanqueador', blanqueador), ('fina', fina),
                ('jabon', jabon), ('perfume', perfume),
                ('quitamancha', quitamancha), ('color', color),
                ('suavizante', suavizante)])


def limpieza_del_bano():
    # origen
    origen = Categoria.objects.get(id=776)

    # destinos
    bano = Categoria.objects.get(id=598)   # Baño

    mover(origen, intento_borrar=True, default=bano)


def limpieza_del_calzado():
    # origen
    origen = Categoria.objects.get(id=897)

    # destinos
    pomada = Categoria.objects.get(id=572)   # Pomada
    mover(origen, intento_borrar=True, default=pomada)


def limpieza_del_hogar():
    # origen
    origen = Categoria.objects.get(id=924)

    # destinos
    bano = Categoria.objects.get(id=598)   # Baño
    cocina = Categoria.objects.get(id=599)   # Cocina
    piso = Categoria.objects.get(id=600)   # Pisos
    mueble = Categoria.objects.get(id=601)   # Placard- muebles
    multiuso = Categoria.objects.get(id=602)   # Vidrios- multiuso

    mover(origen, intento_borrar=True, default=multiuso,
          mapa=[('bano', bano), ('cocina', cocina),
                ('piso', piso), ('mueble', mueble),
                ('multiuso', multiuso)])


def locion_antimosquito():
    # origen
    origen = Categoria.objects.get(id=946)

    # destinos
    cucaracha = Categoria.objects.get(id=593)   # Cucarachas
    hormiga = Categoria.objects.get(id=594)   # Hormigas
    mosquito = Categoria.objects.get(id=595)   # Moscas y mosquitos
    pulga = Categoria.objects.get(id=596)   # Polillas y pulgas
    repelente = Categoria.objects.get(id=597)   # Repelentes

    mover(origen, intento_borrar=True, default=repelente,
          mapa=[('cucaracha', cucaracha), ('hormiga', hormiga),
                ('mosquito', mosquito), ('pulga', pulga),
                ('repelente', repelente)])


def lustra_metales():
    # origen
    origen = Categoria.objects.get(id=819)

    # destinos
    vario = Categoria.objects.get(id=622)   # Varios

    mover(origen, intento_borrar=True, default=vario)


def lustra_muebles():
    # origen
    origen = Categoria.objects.get(id=922)

    # destinos
    mover(origen, intento_borrar=True, default=Categoria.objects.get(id=603))


def lamparas():
    # origen
    origen = Categoria.objects.get(id=799)

    # destinos
    lamparita = Categoria.objects.get(id=434)   # Lamparitas
    bajo = Categoria.objects.get(id=963)   # Bajo Consumo

    mover(origen, intento_borrar=True, default=lamparita,
          mapa=[('bajo', bajo)])


def maltas():
    # origen
    origen = Categoria.objects.get(id=823)

    # destinos
    malta = Categoria.objects.get(id=961)   # Maltas

    mover(origen, intento_borrar=True, default=malta)


def manos_y_unas():
    # origen
    origen = Categoria.objects.get(id=791)

    # destinos
    accesorio = Categoria.objects.get(id=699)   # Accesorios
    crema = Categoria.objects.get(id=700)   # Cremas
    esmalte = Categoria.objects.get(id=701)   # Esmaltes
    quitaesmalte = Categoria.objects.get(id=702)   # Quitaesmalte

    mover(origen, intento_borrar=True, default=crema,
          mapa=[('accesorio', accesorio), ('crema', crema),
                ('esmalte', esmalte), ('quitaesmalte', quitaesmalte)])


def mantecas_y_margarinas():
    # origen
    origen = Categoria.objects.get(id=777)

    # destinos
    manteca = Categoria.objects.get(id=512)   # Mantecas
    margarina = Categoria.objects.get(id=513)   # Margarinas

    mover(origen, intento_borrar=True, default=manteca,
          mapa=[('manteca', manteca), ('margarina', margarina)])


def mascotas():
    # origen
    origen = Categoria.objects.get(id=865)

    # destinos
    gato_adulto = Categoria.objects.get(id=639)   # Adulto
    gato_cachorro = Categoria.objects.get(id=640)   # Cachorro
    perro_adulto = Categoria.objects.get(id=641)   # Adulto
    cachorro = Categoria.objects.get(id=642)      # Cachorro

    mover(origen, intento_borrar=True, default=perro_adulto,
          mapa=[('gato', gato_adulto), ('gatito', gato_cachorro),
                ('cachorro', cachorro)])


def mate_cocido():
    # origen
    origen = Categoria.objects.get(id=778)

    # destinos
    cocido = Categoria.objects.get(id=282)   # Mate cocido
    mover(origen, intento_borrar=True, default=cocido)


def medallones_de_pollo():
    # origen
    origen = Categoria.objects.get(id=785)

    # destinos
    pollo = Categoria.objects.get(id=413)   # Pollo

    mover(origen, intento_borrar=True, default=pollo)


def milanesas_de_soja():
    # origen
    origen = Categoria.objects.get(id=932)

    # destinos
    soja = Categoria.objects.get(id=414)   # Soja
    mover(origen, intento_borrar=True, default=soja)


def otras_bebidas_con_alcohol():
    # origen
    origen = Categoria.objects.get(id=923)

    # destinos
    bivarietal = Categoria.objects.get(id=369)   # Bivarietal
    borgona = Categoria.objects.get(id=370)   # Borgoña
    sauvignon = Categoria.objects.get(id=371)   # Cabernet sauvignon
    malbec = Categoria.objects.get(id=372)   # Malbec
    merlot = Categoria.objects.get(id=373)   # Merlot
    cepa = Categoria.objects.get(id=374)   # Otras cepas
    syrah = Categoria.objects.get(id=375)   # Syrah
    tempranillo = Categoria.objects.get(id=376)   # Tempranillo
    whisky = Categoria.objects.get(id=958)   # Blancas

    blancas = Categoria.objects.get(id=352)   # Blancas

    mover(origen, intento_borrar=True, default=blancas,
          mapa=[('bivarietal', bivarietal), ('wisky', whisky), ('whisky', whisky),
                ('borgona', borgona), ('sauvignon', sauvignon), ('malbec', malbec),
                ('merlot', merlot), ('cepa', cepa), ('syrah', syrah),
                ('tempranillo', tempranillo)])


def otras_bebidas_sin_alcohol():
    # origen
    origen = Categoria.objects.get(id=783)

    # destinos
    hierba = Categoria.objects.get(id=387)   # Amargos / Hierbas

    mover(origen, intento_borrar=True,
          mapa=[('hierba', hierba)])


def otros_alimentos_congelados():
    # origen
    origen = Categoria.objects.get(id=939)

    # destinos
    pescado = Categoria.objects.get(id=412)   # Pescado
    pollo = Categoria.objects.get(id=413)   # Pollo
    soja = Categoria.objects.get(id=414)   # Soja
    verdura = Categoria.objects.get(id=415)   # Verdura
    vegetales = Categoria.objects.get(id=416)   # Verdura

    mover(origen, intento_borrar=True, default=vegetales,
          mapa=[('pescado', pescado), ('pollo', pollo),
                ('soja', soja), ('verdura', verdura)])


def otros_limpiadores_desinfectantes():
    # origen
    origen = Categoria.objects.get(id=901)

    # destinos
    bano = Categoria.objects.get(id=598)   # Baño
    cocina = Categoria.objects.get(id=599)   # Cocina
    piso = Categoria.objects.get(id=600)   # Pisos
    mueble = Categoria.objects.get(id=601)   # Placard- muebles
    multiuso = Categoria.objects.get(id=602)   # Vidrios- multiuso

    mover(origen, intento_borrar=True, default=multiuso,
          mapa=[('bano', bano), ('cocina', cocina),
                ('piso', piso), ('mueble', mueble), ('multiuso', multiuso)])


def otros_panes():
    # origen
    origen = Categoria.objects.get(id=773)

    # destinos
    vario = Categoria.objects.get(id=643)   # Varios

    mover(origen, intento_borrar=True, default=vario)


def otros_productos_frescos():
    # origen
    origen = Categoria.objects.get(id=780)

    # destinos
    aerosol = Categoria.objects.get(id=226)   # Aerosol
    otro = Categoria.objects.get(id=227)   # Canola- otros
    girasol = Categoria.objects.get(id=228)   # Girasol
    maiz = Categoria.objects.get(id=229)   # Maiz
    mezcla = Categoria.objects.get(id=230)   # Mezcla
    oliva = Categoria.objects.get(id=231)   # Oliva

    mover(origen, intento_borrar=True,
          mapa=[('aerosol', aerosol), ('otro', otro),
                ('girasol', girasol), ('maiz', maiz), ('mezcla', mezcla),
                ('oliva', oliva)])


def otros_productos_de_limpieza():
    # origen
    origen = Categoria.objects.get(id=781)

    escobillone = Categoria.objects.get(id=590)   # Escobillones
    mover(origen, intento_borrar=True, default=escobillone)


def otros_productos_para_bebes():
    # origen
    origen = Categoria.objects.get(id=807)

    # destinos
    mamadera = Categoria.objects.get(id=960)   # Chupetes/ mamaderas

    mover(origen, intento_borrar=True,
          mapa=[('mamadera', mamadera)])


def otros_productos_para_el_hogar():
    # origen
    origen = Categoria.objects.get(id=920)

    # destinos
    adulto = Categoria.objects.get(id=641)   # Adulto
    cachorro = Categoria.objects.get(id=642)   # Cachorro

    mover(origen, intento_borrar=True,
          mapa=[('adulto', adulto), ('cachorro', cachorro)])


def pan_dulce():
    # origen
    origen = Categoria.objects.get(id=909)

    # destinos
    budines = Categoria.objects.get(id=290)   # Budines/otros

    mover(origen, intento_borrar=True, default=budines)


def pan_integral():
    # origen
    origen = Categoria.objects.get(id=867)
    # destinos
    default = Categoria.objects.get(id=959)   # integral
    mover(origen, intento_borrar=True, default=default)


def pan_lacteado():
    # origen
    origen = Categoria.objects.get(id=837)

    # destinos
    default = Categoria.objects.get(id=962)   # lactal/lacteado
    mover(origen, intento_borrar=True, default=default)


def pan_de_cereal():
    # origen
    origen = Categoria.objects.get(id=889)
    default = Categoria.objects.get(id=960)   # integral
    mover(origen, intento_borrar=True, default=default)


def pan_de_mesa():
    # origen
    origen = Categoria.objects.get(id=907)
    # destinos
    propia = Categoria.objects.get(id=292)
    mover(origen, intento_borrar=True, default=propia)


def pan_de_salvado():
    # origen
    origen = Categoria.objects.get(id=794)
    default = Categoria.objects.get(id=960)   # integral
    mover(origen, intento_borrar=True, default=default)


def pan_para_hamburguesas():
    # origen
    origen = Categoria.objects.get(id=854)

    pancho = Categoria.objects.get(id=291)   # Hamb/ panchos

    mover(origen, intento_borrar=True, default=pancho)


def pan_para_panchos():
    # origen
    origen = Categoria.objects.get(id=840)
    # destinos
    pancho = Categoria.objects.get(id=291)   # Hamb/ panchos
    mover(origen, intento_borrar=True, default=pancho)


def pan_arabe():
    # origen
    origen = Categoria.objects.get(id=838)

    # destinos
    arabe = Categoria.objects.get(id=289)   # Arabe

    mover(origen, intento_borrar=True, default=arabe)


def panificados():
    # origen
    origen = Categoria.objects.get(id=851)

    # destinoinos
    vario = Categoria.objects.get(id=643)   # Varios

    mover(origen, intento_borrar=True, default=vario)


def papas_fritas():
    # origen
    origen = Categoria.objects.get(id=930)
    # destinos
    frita = Categoria.objects.get(id=411)   # Papas fritas
    mover(origen, intento_borrar=True, default=frita)


def papeles_higienicos():
    # origen
    origen = Categoria.objects.get(id=894)

    # destinos
    higienico = Categoria.objects.get(id=607)   # Papel higienico

    mover(origen, intento_borrar=True, default=higienico)


def pastas():
    # origen
    origen = Categoria.objects.get(id=863)

    # destinos
    guisero = Categoria.objects.get(id=295)   # Guiseros
    otro = Categoria.objects.get(id=296)   # Integrales- otros
    largo = Categoria.objects.get(id=297)   # Largos
    otra = Categoria.objects.get(id=298)   # Rellenas- otras
    sopero = Categoria.objects.get(id=299)   # Soperos

    mover(origen, intento_borrar=True, default=otra,
          mapa=[('guisero', guisero),
                ('tirabuzon', guisero),
                ('otro', otro),
                ('largo', largo),
                ('tallarin', largo),
                ('raviol', otra),
                ('sopero', sopero)])


def pastas_frescas():
    # origen
    origen = Categoria.objects.get(id=941)

    # destinos
    fideo = Categoria.objects.get(id=645)   # Fideos
    noqui = Categoria.objects.get(id=646)   # Noquis
    rellena = Categoria.objects.get(id=647)   # Rellenas

    mover(origen, intento_borrar=True, default=rellena,
          mapa=[('fideo', fideo), ('noqui', noqui), ('rellena', rellena)])


def pastas_secas():
    # origen
    origen = Categoria.objects.get(id=841)

    # destinos
    guisero = Categoria.objects.get(id=295)   # Guiseros
    otro = Categoria.objects.get(id=296)   # Integrales- otros
    largo = Categoria.objects.get(id=297)   # Largos
    otra = Categoria.objects.get(id=298)   # Rellenas- otras
    sopero = Categoria.objects.get(id=299)   # Soperos

    mover(origen, intento_borrar=True, default=otro,
          mapa=[('guisero', guisero), ('otro', otro),
                ('largo', largo), ('otra', otra), ('sopero', sopero)])


def panales_descartables():
    # origen
    origen = Categoria.objects.get(id=944)

    # destinos
    g = Categoria.objects.get(id=954)   # Medida G
    m = Categoria.objects.get(id=955)   # Medida M
    p = Categoria.objects.get(id=957)   # Medida P
    xg = Categoria.objects.get(id=943)   # Medida XG

    mover(origen, intento_borrar=True, default=m,
          mapa=[(' G ', g), (' M ', m), (' P ', p), (' XG ', xg)])


def panales_para_adultos():
    # origen
    origen = Categoria.objects.get(id=789)

    # destinos
    destino = Categoria.objects.get(id=964)   # Adultos

    mover(origen, intento_borrar=True, default=destino)


def panos_multiuso_y_trapos_de_piso():
    # origen
    origen = Categoria.objects.get(id=792)

    # destinos
    limpiadore = Categoria.objects.get(id=610)   # Limpiadores
    secadore = Categoria.objects.get(id=611)   # Secadores
    mopa = Categoria.objects.get(id=612)   # Trapos- mopas

    mover(origen, intento_borrar=True,
          mapa=[('limpiadore', limpiadore), ('secadore', secadore), ('mopa', mopa)])


def panuelos_descartables():
    # origen
    origen = Categoria.objects.get(id=879)

    # destinos
    higienico = Categoria.objects.get(id=607)   # Papel higienico
    panuelo = Categoria.objects.get(id=606)   # Pañuelos
    cocina = Categoria.objects.get(id=608)   # Rollo de cocina
    servilleta = Categoria.objects.get(id=609)   # Servilletas

    mover(origen, intento_borrar=True,
          mapa=[('higienico', higienico),
                ('panuelo', panuelo), ('cocina', cocina),
                ('servilleta', servilleta)])


def pegamentos():
    # origen
    origen = Categoria.objects.get(id=866)

    # destinos
    adhesivo = Categoria.objects.get(id=428)   # Adhesivos

    mover(origen, intento_borrar=True,
          mapa=[('adhesivo', adhesivo)])


def pilas():
    # origen
    origen = Categoria.objects.get(id=870)

    # destinos
    pila = Categoria.objects.get(id=435)   # Pilas

    mover(origen, intento_borrar=True,
          mapa=[('pila', pila)])


def pionono():
    # origen
    origen = Categoria.objects.get(id=884)

    # destinos
    otro = Categoria.objects.get(id=290)   # Budines/otros
    mover(origen, intento_borrar=True, default=otro)


def pizzas():
    # origen
    origen = Categoria.objects.get(id=808)

    # destinos
    empanada = Categoria.objects.get(id=403)   # Empanadas
    otro = Categoria.objects.get(id=404)   # Otros
    pizza = Categoria.objects.get(id=405)   # Pizzas

    mover(origen, intento_borrar=True,
          mapa=[('empanada', empanada), ('otro', otro), ('pizza', pizza)])


def plumeros():
    # origen
    origen = Categoria.objects.get(id=828)

    # destinos
    limpiavidrio = Categoria.objects.get(id=613)   # Plumeros- limpiavidrios

    mover(origen, intento_borrar=True,
          mapa=[('limpiavidrio', limpiavidrio)])


def polvo_de_fecula_y_talco_para_bebes():
    # origen
    origen = Categoria.objects.get(id=926)

    # destinos
    fecula = Categoria.objects.get(id=635)   # Talco/ fecula

    mover(origen, intento_borrar=True,
          mapa=[('fecula', fecula)])


def polvos_instantaneos():
    # origen
    origen = Categoria.objects.get(id=817)

    # destinos
    flane = Categoria.objects.get(id=300)   # Flanes
    gelatina = Categoria.objects.get(id=301)   # Gelatinas
    helado = Categoria.objects.get(id=302)   # Helados
    postre = Categoria.objects.get(id=303)   # Postres

    mover(origen, intento_borrar=True, default=postre,
          mapa=[('flan', flane), ('gelatina', gelatina),
                ('helado', helado), ('postre', postre)])


def postres_frios():
    # origen
    origen = Categoria.objects.get(id=811)

    # destinos
    flane = Categoria.objects.get(id=300)   # Flanes
    gelatina = Categoria.objects.get(id=301)   # Gelatinas
    helado = Categoria.objects.get(id=302)   # Helados
    postre = Categoria.objects.get(id=303)   # Postres

    mover(origen, intento_borrar=True, default=helado,
          mapa=[('flan', flane), ('gelatina', gelatina),
                ('helado', helado), ('postre', postre)])


def postres_instantaneos():
    # origen
    origen = Categoria.objects.get(id=848)

    # destinos
    flane = Categoria.objects.get(id=300)   # Flanes
    gelatina = Categoria.objects.get(id=301)   # Gelatinas
    helado = Categoria.objects.get(id=302)   # Helados
    postre = Categoria.objects.get(id=303)   # Postres

    mover(origen, intento_borrar=True, default=postre,
          mapa=[('flane', flane), ('gelatina', gelatina),
                ('helado', helado), ('postre', postre)])


def prepizzas():
    # origen
    origen = Categoria.objects.get(id=903)

    # destinos
    vario = Categoria.objects.get(id=643)   # Varios

    mover(origen, intento_borrar=True, default=vario)


def preservativos():
    # origen
    origen = Categoria.objects.get(id=786)

    # destinos
    preservativo = Categoria.objects.get(id=688)   # Preservativos

    mover(origen, intento_borrar=True, default=preservativo)


def proteccion_femenina():
    # origen
    origen = Categoria.objects.get(id=779)

    # destinos
    femenina = Categoria.objects.get(id=703)   # Higiene femenina
    diario = Categoria.objects.get(id=704)   # Prot diarios
    tampone = Categoria.objects.get(id=705)   # Tampones
    toallita = Categoria.objects.get(id=706)   # Toallitas

    mover(origen, intento_borrar=True, default=femenina,
          mapa=[('femenina', femenina), ('diario', diario), ('tampon', tampone),
                ('toallita', toallita)])


def protectores_mamarios():
    # origen
    origen = Categoria.objects.get(id=774)
    # destinos
    femenina = Categoria.objects.get(id=703)   # Higiene femenina
    mover(origen, intento_borrar=True, default=femenina)


def protesis_dentales():
    # origen
    origen = Categoria.objects.get(id=844)

    # destinos
    adhesivo = Categoria.objects.get(id=675)   # Adhesivos
    cepillo = Categoria.objects.get(id=676)   # Cepillos
    crema = Categoria.objects.get(id=677)   # Cremas
    enjuague = Categoria.objects.get(id=678)   # Enjuagues
    hilo = Categoria.objects.get(id=679)   # Hilo

    mover(origen, intento_borrar=True, default=adhesivo,
          mapa=[('adhesivo', adhesivo), ('cepillo', cepillo),
                ('crema', crema), ('enjuague', enjuague), ('hilo', hilo)])


def pure_instantaneos():
    # origen
    origen = Categoria.objects.get(id=925)

    # destinos
    instantaneo = Categoria.objects.get(id=304)   # Pure instantaneo

    mover(origen, intento_borrar=True, default=instantaneo)


def quesos():
    # origen
    origen = Categoria.objects.get(id=825)

    # destinos
    blando = Categoria.objects.get(id=452)   # Blandos
    duro = Categoria.objects.get(id=453)   # Duros
    especiale = Categoria.objects.get(id=454)   # Especiales
    light = Categoria.objects.get(id=455)   # Light
    untable = Categoria.objects.get(id=456)   # Quesos untables
    rallado = Categoria.objects.get(id=457)   # Rallados
    semiduro = Categoria.objects.get(id=458)   # Semiduros

    mover(origen, intento_borrar=True, default=blando,
          mapa=[('blando', blando), ('duro', duro),
                ('especial', especiale), ('light', light),
                ('untable', untable), ('rallado', rallado), ('semiduro', semiduro)])


def quesos_rallados():
    # origen
    origen = Categoria.objects.get(id=929)

    # destinos
    rallado = Categoria.objects.get(id=457)   # Rallados

    mover(origen, intento_borrar=True, default=rallado)


def quesos_untables():
    # origen
    origen = Categoria.objects.get(id=876)

    # destinos
    untable = Categoria.objects.get(id=456)   # Quesos untables

    mover(origen, intento_borrar=True, default=untable)


def rebozadores():
    # origen
    origen = Categoria.objects.get(id=880)

    # destinos
    rallado = Categoria.objects.get(id=293)   # Pan rallado

    mover(origen, intento_borrar=True, default=rallado)


def reposteria_y_golosinas():
    # origen
    return
    """

    origen = Categoria.objects.get(id=847)

    # destinos
    chocolate = Categoria.objects.get(id=466)   # Chocolate
    hojaldre = Categoria.objects.get(id=467)   # Hojaldre
    madalena = Categoria.objects.get(id=468)   # Madalenas
    rellena = Categoria.objects.get(id=469)   # Rellenas
    seca = Categoria.objects.get(id=470)   # Secas

    mover(origen, intento_borrar=True,
          mapa=[('chocolate', chocolate), ('hojaldre', hojaldre),
                ('madalena', madalena), ('rellena', rellena), ('seca', seca)])
    """


def salchichas():
    # origen
    origen = Categoria.objects.get(id=936)

    # destinos
    salchicha = Categoria.objects.get(id=444)   # Salchichas

    mover(origen, intento_borrar=True, default=salchicha)


def salsas():
    # origen
    origen = Categoria.objects.get(id=830)

    # destinos
    salsa = Categoria.objects.get(id=316)   # Salsas
    tomate = Categoria.objects.get(id=317)   # Tomates

    mover(origen, intento_borrar=True, default=salsa,
          mapa=[('tomate', tomate)])


def salteados():
    # origen
    origen = Categoria.objects.get(id=822)

    # destinos
    vegetale = Categoria.objects.get(id=266)   # Vegetales

    mover(origen, intento_borrar=True, default=vegetale)


def seguridad_para_el_bebe():
    # origen
    origen = Categoria.objects.get(id=800)
    # destinos
    seguridad = Categoria.objects.get(id=634)   # Seguridad
    mover(origen, intento_borrar=True, default=seguridad)


def shampoo():
    # origen
    origen = Categoria.objects.get(id=826)

    # destinos
    cabello = Categoria.objects.get(id=660)   # Accesorios cabello
    acondicionador = Categoria.objects.get(id=661)   # Acondicionador
    coloracion = Categoria.objects.get(id=662)   # Coloracion
    trat = Categoria.objects.get(id=663)   # Crema de peinar- trat
    fijacion = Categoria.objects.get(id=664)   # Gel y fijacion
    infantil = Categoria.objects.get(id=665)   # Infantil
    shampoo = Categoria.objects.get(id=666)   # Shampoo
    caida = Categoria.objects.get(id=667)   # Tratamiento control caida
    pediculosi = Categoria.objects.get(id=668)   # Tratamiento pediculosis
    caspa = Categoria.objects.get(id=669)   # Tratamientos anti caspa

    mover(origen, intento_borrar=True, default=shampoo,
          mapa=[('accesorio', cabello), ('acondicionador', acondicionador),
                ('coloracion', coloracion), ('trat', trat),
                ('fijacion', fijacion), ('infantil', infantil),
                ('shampoo', shampoo), ('caida', caida),
                ('pediculosi', pediculosi), ('caspa', caspa)])


def shampoo_y_crema_de_enjuague_para_bebes():
    # origen
    origen = Categoria.objects.get(id=843)
    # destinos
    shampoo = Categoria.objects.get(id=952)   # Shampoo para bebés
    enjuague = Categoria.objects.get(id=951)   #
    mover(origen, intento_borrar=True, default=shampoo,
          mapa=[('enjuague', enjuague)])


def sidras():
    # origen
    origen = Categoria.objects.get(id=802)

    # destinos
    otro = Categoria.objects.get(id=360)   # Sidras- otros

    mover(origen, intento_borrar=True, default=otro)


def snacks():
    # origen
    origen = Categoria.objects.get(id=886)

    # destinos
    seca = Categoria.objects.get(id=308)   # Frutas secas
    mani = Categoria.objects.get(id=309)   # Mani
    palito = Categoria.objects.get(id=310)   # Palitos
    papa = Categoria.objects.get(id=311)   # Papas
    otro = Categoria.objects.get(id=312)   # Pochoclos- otros

    mover(origen, intento_borrar=True, default=otro,
          mapa=[('seca', seca), ('mani', mani), ('palito', palito),
                ('papa', papa), ('otro', otro)])


def sopas():
    # origen
    origen = Categoria.objects.get(id=916)

    # destinos
    caldo = Categoria.objects.get(id=313)   # Caldos
    saborizadore = Categoria.objects.get(id=314)   # Saborizadores
    sopa = Categoria.objects.get(id=315)   # Sopas

    mover(origen, intento_borrar=True, default=sopa,
          mapa=[('caldo', caldo), ('saborizadore', saborizadore), ('sopa', sopa)])


def tapas():
    # origen
    origen = Categoria.objects.get(id=787)

    # destinos
    empanada = Categoria.objects.get(id=648)   # Empanadas
    otra = Categoria.objects.get(id=649)   # Otras
    tarta = Categoria.objects.get(id=650)   # Tartas

    mover(origen, intento_borrar=True,
          mapa=[('empanada', empanada), ('otra', otra), ('tarta', tarta)])


def tartas():
    # origen
    origen = Categoria.objects.get(id=900)

    # destinos
    empanada = Categoria.objects.get(id=403)   # Empanadas
    otro = Categoria.objects.get(id=404)   # Otros
    pizza = Categoria.objects.get(id=405)   # Pizzas

    mover(origen, intento_borrar=True, default=otro,
          mapa=[('empanada', empanada), ('otro', otro), ('pizza', pizza)])


def toallitas_humedas():
    # origen
    origen = Categoria.objects.get(id=921)

    # destinos
    humeda = Categoria.objects.get(id=636)   # Toallitas humedas

    mover(origen, intento_borrar=True, default=humeda)


def tostadas():
    # origen
    origen = Categoria.objects.get(id=850)

    # destinos
    tostada = Categoria.objects.get(id=294)   # Tostadas
    mover(origen, intento_borrar=True, default=tostada)


def te():
    # origen
    origen = Categoria.objects.get(id=905)
    te = Categoria.objects.get(id=283)   # Te
    mover(origen, intento_borrar=True, default=te)


def vajilla_para_bebes():
    # origen
    origen = Categoria.objects.get(id=821)

    # destinos
    accesorio = Categoria.objects.get(id=637)   # Accesorios

    mover(origen, intento_borrar=True, default=accesorio)


def vegetales():
    # origen
    origen = Categoria.objects.get(id=827)

    # destinos
    vegetale = Categoria.objects.get(id=416)   # Vegetales

    mover(origen, intento_borrar=True,
          mapa=[('vegetale', vegetale)])


def velas_aromatizadores():
    # origen
    origen = Categoria.objects.get(id=833)

    # destinos
    vela = Categoria.objects.get(id=582)   # Velas

    mover(origen, intento_borrar=True, default=vela)


def vinos_blancos():
    # origen
    origen = Categoria.objects.get(id=829)

    # destinos
    chardonnay = Categoria.objects.get(id=361)   # Chardonnay
    cepa = Categoria.objects.get(id=362)   # Otras cepas
    blanc = Categoria.objects.get(id=363)   # Sauvignon blanc
    dulce = Categoria.objects.get(id=364)   # Tardio- dulce
    torronte = Categoria.objects.get(id=365)   # Torrontes

    mover(origen, intento_borrar=True,
          mapa=[('chardonnay', chardonnay), ('cepa', cepa), ('blanc', blanc),
                ('dulce', dulce), ('torronte', torronte)])


def vinos_espumantes():
    # origen
    origen = Categoria.objects.get(id=935)

    # destinos
    champagne = Categoria.objects.get(id=356)   # Champagne
    frizante = Categoria.objects.get(id=357)   # Frizantes

    mover(origen, intento_borrar=True,
          mapa=[('champagne', champagne), ('frizante', frizante)])


def vinos_gasificados():
    # origen
    origen = Categoria.objects.get(id=908)

    # destinos
    champagne = Categoria.objects.get(id=356)   # Champagne
    frizante = Categoria.objects.get(id=357)   # Frizantes

    mover(origen, intento_borrar=True,
          mapa=[('champagne', champagne), ('frizante', frizante)])


def vinos_rosados():
    # origen
    origen = Categoria.objects.get(id=928)

    # destinos
    bivarietal = Categoria.objects.get(id=369)   # Bivarietal
    borgona = Categoria.objects.get(id=370)   # Borgoña
    sauvignon = Categoria.objects.get(id=371)   # Cabernet sauvignon
    malbec = Categoria.objects.get(id=372)   # Malbec
    merlot = Categoria.objects.get(id=373)   # Merlot
    cepa = Categoria.objects.get(id=374)   # Otras cepas
    syrah = Categoria.objects.get(id=375)   # Syrah
    tempranillo = Categoria.objects.get(id=376)   # Tempranillo

    mover(origen, intento_borrar=True, default=cepa,
          mapa=[('bivarietal', bivarietal), ('borgona', borgona),
                ('sauvignon', sauvignon), ('malbec', malbec), ('merlot', merlot),
                ('cepa', cepa), ('syrah', syrah),
                ('tempranillo', tempranillo)])


def vinos_tintos():
    # origen
    origen = Categoria.objects.get(id=873)

    # destinos
    bivarietal = Categoria.objects.get(id=369)   # Bivarietal
    borgona = Categoria.objects.get(id=370)   # Borgoña
    sauvignon = Categoria.objects.get(id=371)   # Cabernet sauvignon
    malbec = Categoria.objects.get(id=372)   # Malbec
    merlot = Categoria.objects.get(id=373)   # Merlot
    syrah = Categoria.objects.get(id=375)   # Syrah
    tempranillo = Categoria.objects.get(id=376)   # Tempranillo
    cepa = Categoria.objects.get(id=374)   # Otras cepas

    mover(origen, intento_borrar=True,
          mapa=[('bivarietal', bivarietal),
                ('borgona', borgona),
                ('sauvignon', sauvignon),
                ('malbec', malbec),
                ('merlot', merlot),
                ('syrah', syrah),
                ('tempranillo', tempranillo)], default=cepa)


def whiskys():
    # origen
    origen = Categoria.objects.get(id=810)

    # destinos
    whisky = Categoria.objects.get(id=958)   # Blancas

    mover(origen, intento_borrar=True, default=whisky)


def yerba_mate():
    # origen
    origen = Categoria.objects.get(id=815)

    # destinos
    yerba = Categoria.objects.get(id=284)   # Yerba

    mover(origen, intento_borrar=True, default=yerba)


def yogurts():
    # origen
    origen = Categoria.objects.get(id=853)

    # destinos
    bebible = Categoria.objects.get(id=521)   # Bebible
    fruta = Categoria.objects.get(id=522)   # Cereal/ frutas
    batido = Categoria.objects.get(id=523)   # Firme/ batido

    mover(origen, intento_borrar=True, default=batido,
          mapa=[('bebible', bebible),
                ('fruta', fruta),
                ('cereal', fruta),
                ('batido', batido)])


def main(paso):
    aceites()
    vinagre_aceto()
    aceitunas()
    aceite_para_bebes()
    acondicionador()
    aderezos()
    afeitado()
    aguas()
    aguas_saborizadas()
    ahumados()
    algodon()
    amargos()
    aperitivos()
    arroz()
    azucar_y_endulzantes()
    bazar()
    bebidas_blancas()
    bebidas_energizantes()
    bebidas_fizz()
    bebidas_isotonicas()
    bizcochos()
    bocaditos()
    bolsas_para_residuos()
    brownies_y_budines()
    cacao_en_polvo()
    cafe()
    caldos_y_saborizadores()
    cepillos_dentales()
    cereales()
    cervezas()
    chocolates()
    coberturas()
    cocina()
    colonia_para_bebes()
    colonias_y_perfumes()
    comidas_preparadas()
    comidas_para_bebes()
    condimentos_y_especias()
    conservas()
    cremas()
    cremas_corporales()
    cremas_dentales()
    cremas_faciales()
    cuidado_de_la_piel()
    cuidado_del_cabello()
    depilacion()
    desodorantes()
    desodorantes_de_ambientes()
    destapacanerias()
    dulces()
    emulsiones_limpiadoras_para_bebes()
    enjuagues_bucales()
    escobas_escobillones_y_cepillos()
    esponjas()
    farmacia()
    fiambres_y_embutidos()
    frutas()
    galletas_y_galletitas()
    gaseosas()
    gel_de_ducha()
    grisines()
    guantes_multiuso()
    hamburguesas()
    harinas()
    helados_y_postres()
    hilo_dental()
    hisopos()
    huevos()
    infusiones()
    insecticidas_y_repelentes()
    jabones_y_banos_liquidos()
    jabones_y_banos_liquidos_para_bebes()
    jugos()
    jugos_en_polvo()
    lavandinas()
    leche()
    leche_en_polvo()
    leche_y_formulas_para_bebes()
    levaduras()
    libreria_y_oficinas()
    licores()
    limpiador_de_vidrios_y_multiusos()
    limpieza_facial()
    limpieza_de_pisos()
    limpieza_de_la_cocina()
    limpieza_de_la_ropa()
    limpieza_del_bano()
    limpieza_del_calzado()
    limpieza_del_hogar()
    locion_antimosquito()
    lustra_metales()
    lustra_muebles()
    lamparas()
    maltas()
    manos_y_unas()
    mantecas_y_margarinas()
    mascotas()
    mate_cocido()
    medallones_de_pollo()
    milanesas_de_soja()
    otras_bebidas_con_alcohol()
    otras_bebidas_sin_alcohol()
    otros_alimentos_congelados()
    otros_limpiadores_desinfectantes()
    otros_panes()
    otros_productos_frescos()
    otros_productos_de_limpieza()
    otros_productos_para_bebes()
    otros_productos_para_el_hogar()
    pan_dulce()
    pan_integral()
    pan_lacteado()
    pan_de_cereal()
    pan_de_mesa()
    pan_de_salvado()
    pan_para_hamburguesas()
    pan_para_panchos()
    pan_arabe()
    panificados()
    papas_fritas()
    papeles_higienicos()
    pastas()
    pastas_frescas()
    pastas_secas()
    panales_descartables()
    panales_para_adultos()
    panos_multiuso_y_trapos_de_piso()
    panuelos_descartables()
    pegamentos()
    pilas()
    pionono()
    pizzas()
    plumeros()
    polvo_de_fecula_y_talco_para_bebes()
    polvos_instantaneos()
    postres_frios()
    postres_instantaneos()
    prepizzas()
    preservativos()
    proteccion_femenina()
    protectores_mamarios()
    protesis_dentales()
    pure_instantaneos()
    quesos()
    quesos_rallados()
    quesos_untables()
    rebozadores()
    reposteria_y_golosinas()
    salchichas()
    salsas()
    salteados()
    seguridad_para_el_bebe()
    shampoo()
    shampoo_y_crema_de_enjuague_para_bebes()
    sidras()
    snacks()
    sopas()
    tapas()
    tartas()
    toallitas_humedas()
    tostadas()
    te()
    vajilla_para_bebes()
    vegetales()
    velas_aromatizadores()
    vinos_blancos()
    vinos_espumantes()
    vinos_gasificados()
    vinos_rosados()
    vinos_tintos()
    whiskys()
    yerba_mate()
    yogurts()


if __name__ == '__main__':
    main()
