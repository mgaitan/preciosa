Instalación de la plataforma
============================

Preciosa es una aplicación web basada en Django_ y Geodjango_. Como depende de una `base de dato espacial <http://es.wikipedia.org/wiki/Base_de_datos_espacial>`_ (en particular, usamos PostGis_) y de muchos otros componentes, no es trivial (pero tampoco difícil) armar un entorno de programación.

Esta sección describe distintos modos, dependiendo el sistema operativo y el objetivo de la instalación.

Para la configuración de un entorno de desarrollo rápido, la recomendación es utilizar Vagrant.

.. toctree::
   :maxdepth: 2

   install_vagrant
   install_dev_linux
   install_dev_mac
   install_dev_windows
   install_produccion



.. _Django: https://djangoproject.com
.. _Geodjango: https://docs.djangoproject.com/en/dev/ref/contrib/gis/
.. _PostGis: http://www.postgis.org/

