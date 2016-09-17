Instalación de la plataforma
============================

Preciosa es una aplicación web basada en Django_ y Geodjango_. Como depende de una `base de dato espacial <http://es.wikipedia.org/wiki/Base_de_datos_espacial>`_ (en particular, usamos PostGis_) y de muchos otros componentes, no es trivial (pero tampoco difícil) armar un entorno de desarrollo.

Por ello, la manera recomendada es utilizar docker


1. Forkear y clonar el código del repositorio
2. Instalar `docker-compose <https://docs.docker.com/compose/install/>`_ de la manera correspondiente y conveniente a tu sistema operativo.
3. Construir el contenedor ejecutando ``docker-compose build web``.
4. Inicializar la base de datos ``docker-compose run web initialize.db``

ya podés empezar a programar!

Para "levantar" el contenedor de preciosa bastará hacer  ``docker-compose up``.
Tu servidor de desarrollo quedará disponible en http://localhost:8000

.. attention:: Recordá que para correr cualquier comando dentro del contenedor
               debés precederlo con ``docker-compose run web``
               Por ejemplo, para ejecutar el shell de django::

                    docker-compose run web python manage.py shell


.. _Django: https://djangoproject.com
.. _Geodjango: https://docs.djangoproject.com/en/dev/ref/contrib/gis/
.. _PostGis: http://www.postgis.org/

