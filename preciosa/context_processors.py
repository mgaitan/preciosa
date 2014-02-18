from precios.models import Categoria


def menu(request):
    # hasta cerrar #64 excluyo la categoria A CLASIFICAR
    return {'menu': Categoria.objects.filter(depth=1).exclude(id=772)}
