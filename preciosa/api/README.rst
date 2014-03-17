Preciosa API v1
================

.. attention::

    la API está en plena fase de diseño e implementación. Puede cambiar
    sin previo aviso

Breve intro a Django Rest Framework
-------------------------------------

La API REST de Preciosa está implementada con `Django Rest Framework`_ (DRF)
Hay 3 módulos que importan

- ``serializers.py``
- ``views.py``
- ``urls.py``

El primero define los *serializadores*, conceptualmente análogos a un
formulario, que dado un objeto (en general, una instancia de un Modelo),
define las reglas de como debe mostrar los atributos en un formato de
representación (como JSON) o, en sentido inverso, como debe recontruir un objecto a partir de una representación.

El segundo módulo define las "vistas", que son similares a las
de Django (aunque el objeto ``Response`` que usa la API es ligeramente distinto). Para los casos de uso más comunes se pueden usar
``Class Based View`` (análogas a las CBV de Django, que saben
listar, mostrar, crear, etc.  objetos/instancias de modelos)
o una abstracciín aún más general denominada ``ViewSet``, que puede pensarse como una *factory* de Class Based Views: un Viewset para un modelo,
ya sabe hacer *todos* los casos comunes y, como yapa, mediante un ``Router``, nos genera **automáticamente** una estructura de urls tipicas.
Por último, puede definirse una vista tipica como función, decorada con
el decorador de DRF ``@api_view

Las urls son iguales a las de cualquier aplicación Django, salvo
por la utilización opcional de un ``router``, que puede considerarse
una *factory* de URLs.

Preciosa utiliza un mix de todas las posilidades de que brinda DRF.
Por ejemplo, los *endpoints* para modelos simples como ``Cadena`` (Walmart, Disco, etc), utilizan ``ViewSets``, algunos listados/detalles como el del modelo ``Producto`` (que puede accederse en general o para una sucursal en particular) usa ``CBVs`` y la vista de detalle para productos (en una sucursal) usa una vista basada implenentada como función decorada.

.. warning::

    **DISCLAIMER**: Estamos aprendiendo a usar este framework sobre la marcha.
    Si tenés ideas de cómo mejorar, recomendaciones, etc. estaremos contentos
    de recibirlas.

¿que se puede hacer?
--------------------

Como DRF ofrece una versión HTML del contenido de la API, gran parte de los
recursos que la API de preciosa ofrece pueden autodescubrirse navegando
desde la raiz.


    http://preciosdeargentina.com.ar/api/v1/

Otros recursos
--------------

Detalle de una sucursal

   http://preciosdeargentina.com.ar/api/v1/sucursales/<pk>

Listado de productos con precios conocidos en una sucursal

   http://preciosdeargentina.com.ar/api/v1/sucursales/<pk>/productos

Detalle de producto para una sucursal en particular

   http://preciosdeargentina.com.ar/api/v1/sucursales/<pk>/productos

   Este recurso devuelve un **detalle exhaustivo** de los precios probables y los mejores para una zona, incluyendo sucursales asociadas a esos mejores precios.


Filtros
+++++++

El listado de de productos (http://preciosdeargentina.com.ar/api/v1/productos) puede recibir los siguientes parámetros via ``GET``

``q``
    cadena a buscar. Usa el criterio definido en ``Producto.objects.buscar``
    Por ejemplo, puede ser un conjunto de palabras claves o un código de barras.

``limite``
    cuantos resultados mostrar para el criterio

``pk``
    limita la busqueda a un PK de producto en particular


El listado de sucursales (http://preciosdeargentina.com.ar/api/v1/sucursales) puede recibir los siguientes parámetros via ``GET``


``q``

    cadena a buscar en nombre de sucursal o cadena

``lat``, ``lon`` y ``radio``:

   una posición y el radio que determina las zona donde se buscan sucursales.
   Estos parámetros son interdependientes.





.. _Django Rest Framework: http://django-rest-framework.org/
