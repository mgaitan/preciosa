from precios.models import Categoria
from flatpagex.models import FlatPageX


def menu(request):
    tabs = FlatPageX.objects.exclude(status=FlatPageX.STATUS.borrador)
    tabs = tabs.exclude(url='/')
    tabs = tabs.order_by('posicion', 'modified')
    # hasta cerrar #64 excluyo la categoria A CLASIFICAR
    return {'menu': Categoria.objects.filter(depth=1).exclude(oculta=True),
            'tabs': tabs}
