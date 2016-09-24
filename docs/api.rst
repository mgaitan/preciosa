.. _api:

La API de Preciosa
==================

.. attention::

    La API está en plena fase de diseño e implementación.
    Puede cambiar sin previo aviso

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
el decorador de DRF ``@api_view``

Las urls son iguales a las de cualquier aplicación Django, salvo
por la utilización opcional de un ``router`` (una *factory* de URLs).

Preciosa utiliza una mezcla de todas las posilidades de que brinda DRF.

Por ejemplo, los *endpoints* para modelos simples como ``Cadena`` (Walmart, Disco, etc), utilizan ``ViewSets``, algunos listados/detalles como el del modelo ``Producto`` (que puede accederse en general o para una sucursal en particular) usa ``CBVs`` y la vista de detalle para productos (en una sucursal) usa una vista basada implenentada como función decorada.

.. warning::

    **DISCLAIMER**: Estamos aprendiendo a usar este framework sobre la marcha.
    Si tenés ideas de cómo mejorar, recomendaciones, etc. estaremos contentos
    de recibirlas.

Autenticación básica basada en token
------------------------------------

La API de preciosa utiliza una manera muy simple y opcionalmente anónima
de autenticación. El motivo de usar autenticación es para prevenir/aminorar el vandalismo y el uso desleal de los recursos.

Cada usuario está asociado a un token. Registrar un usuario para obtener un token
es muy fácil. Basta hacer un ``POST`` al enpoint

    http://preciosdeargentina.com.ar/api/v1/auth/registro

Opcionalmente la petición puede enviar esta información

``uuid``
    un identificador único del equipo  (ejemplo, el movil)

``nombre``
    un nombre elegido por el usuario para el equipo

``plataforma``
    la plataforma subyacente (ejemplo: "Android")

``phonegap``
    si el cliente es Phonegap, la versión.

``plataforma_version``
    la versión de la plataforma (ejemplo "2.2" para Android)

``preciosa_version``
    la versión del cliente de preciosa.

Los parámetros no son obligatorios, pero cualquiera subconjunto que se envie
debe incluir el ``uuid`` (sin uuid ninguna información quedará guardada)

Obtenido el token, este debe enviarse para cada subsecuente petición. Puede hacerse configurando el un header HTTP. Por ejemplo

    Authorization: Token XXXXX

Donde XXXX es el token dado.

Desde jQuery, puede configurarse para todas las peticiones ajax

.. code-block:: javascript

            $.ajaxSetup({
              headers: {
                'Authorization': "Token XXXXX"
              }
            });

Alternativamente, se puede enviar un token como parámetro en el ``QUERY``
de la URL. Por ejemplo::

    api/v1/<end_point>/?token=XXXX


Si ya se cuenta con un usuario y contraseña (por ejemplo un Voluntario registrado via web) se puede obtener un token enviando parámetros ``usuario`` y ``password`` al recurso

    http://preciosdeargentina.com.ar/api/v1/auth/token

Devuelve el token en formato json de igual manera que ``/auth/registro``


¿Qué se puede hacer?
--------------------

Como DRF ofrece una versión HTML del contenido de la API, gran parte de los
recursos que la API de preciosa ofrece pueden autodescubrirse navegando
desde la raiz.


    http://preciosdeargentina.com.ar/api/v1/

Otros recursos
--------------

Detalle de una sucursal
   ``http://preciosdeargentina.com.ar/api/v1/sucursales/<pk>``

Listado de productos con precios conocidos en una sucursal
   ``http://preciosdeargentina.com.ar/api/v1/sucursales/<pk>/productos``

   Es igual que ``http://preciosdeargentina.com.ar/api/v1/productos``,
   pero filtra aquellos productos en los que para esa sucursal
   hay precios conocidos.

Detalle de producto para una sucursal en particular
   ``http://preciosdeargentina.com.ar/api/v1/sucursales/<pk>/productos/<pk_producto>``

   Este recurso devuelve un **detalle exhaustivo** de los precios probables y los mejores para una zona, incluyendo sucursales asociadas a esos mejores precios.


Filtros
-------

El listado de productos (http://preciosdeargentina.com.ar/api/v1/productos) puede recibir los siguientes parámetros opcionales via ``GET``

``q``
    cadena a buscar. Usa el criterio definido en ``Producto.objects.buscar``
    (es decir, dará los mismos resultados que el buscador de la web).
    Por ejemplo, puede ser un conjunto de palabras claves o un código de barras (completo o los primeros números desde la izquierda).

``limite``
    cuantos resultados mostrar para el criterio

``pk``
    limita la busqueda a un PK de producto en particular


El listado de sucursales (http://preciosdeargentina.com.ar/api/v1/sucursales) puede recibir los siguientes parámetros via ``GET``


``q``
    cadena a buscar. Por ejemplo, nombre de ciudad, cadena, o calle.

``lat``, ``lon`` y ``radio``:
   una posición y el radio en kilometros que determina las zona donde se buscan sucursales. Estos parámetros son interdependientes.


El listado de Ciudades (http://preciosdeargentina.com.ar/api/v1/ciudades)
 puede recibir los siguientes parámetros via ``GET``:

``q``
    cadena a buscar. Por ejemplo, nombre de ciudad o provincia.


Formatos
---------

DRF sabe interpretar el ``content-type`` preferido en el encabezado de la petición ``HTTP``. Alternativamente puede definirse mediante el parámetro
``format``  en la URL del recurso. Por ejemplo

    http://preciosdeargentina.com.ar/api/v1/cadenas/?format=json

Forzará el serializado de la lista de cadenas en formato JSON, aun desde un navegador web que acepta HTML.

Tasas de limitación (throttling)
---------------------------------

Complementario a la autenticación, la API tiene un sistema de
limitación de peticiones (*throttling*), para evitar el abuso de usuarios malintencionados.

Actualmente las tasas son:

- 30 peticiones por dia para usuarios anónimos. Actualmente permite
  acceder a la URL ``/auth/registro``

- 40 peticiones por minuto para usuarios autorizados.
  Es para evitar los picos de peticiones automatizadas.

- 1000 peticiones por dia para usuarios autorizados. Es para evitar
  el "leeching".


.. _Django Rest Framework: http://django-rest-framework.org/
