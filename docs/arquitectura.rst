.. _arquitectura:

Arquitectura
============


Modelo de base de datos
-----------------------

Los modelos fundamentales de Preciosa se definen en la aplicación :file:`precios </preciosa/precios/models.py>`. Un diagrama simplificado es el siguiente:


.. image:: http://yuml.me/d04f8709

.. editar desde http://yuml.me/edit/d04f8709


Algoritmos de "precios"
-----------------------

Como se observa, el relevamiento de un ``precio`` está asociado a un producto y a una sucursal específica (y, opcionalmente, a un usuario), además de su fecha de relevamiento.

Al ser improbable la existencia de precios para cualquier producto en **todas** las sucursales, la consulta del precio de un producto para una sucursal en particular se realiza a través del método :meth:`PrecioManager.mas_probables`, que realiza un degradado de información:

1. Si existe un precio relevado para el producto en la sucursal, dentro del rango de máximo de dias, se devuelve ese dato
2. En caso de que no exista, se buscan precios para el producto en sucursales de la misma cadena o un radio definido.
3. Si no hay precios en Sucursales, se buscan el precio del producto en la "Sucursal Online" de la Cadena.
4. Si no hay sucursal online asociada o no existe un precio vigente, no se devuelve un resultado.


.. literalinclude:: ../preciosa/precios/models.py
   :pyobject: PrecioManager.mas_probables

Análogamente se calculan los mejores precios. Dado un producto, una ubicación (o sucursal) y radio de distancia, se obtiene una lista de los mejores precios en la zona para ese producto.

.. literalinclude:: ../preciosa/precios/models.py
   :pyobject: PrecioManager.mejores
