from precios.models import Categoria


def menu(request):
    return {'menu': Categoria.objects.filter(depth=1).exclude(id=772)}
