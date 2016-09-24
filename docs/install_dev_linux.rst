.. _install_linux:

Creación de un entorno de desarrollo local en Linux
===================================================

El objetivo de este documento es permitir que los desarrolladores puedan
crear sus entornos de desarrollo **en una maquina local**. Esta instalación es para usuarios más avanzados, que prefieren un control particular sobre la instalación o necesitan mayor performance. En cualquier otro caso recomendamos :ref:`vagrant <install_vagrant>`.


Esta guía está pensada principalmente para sistemas Linux Ubuntu/Debian, aunque hay comentarios para otros entornos.


Preparación del entorno
-----------------------

1. Instalación de ``virtualenv``

virtualenv_ nos permite aislar la instalación de paquetes de la instalación del sistema. Es buena práctica utilizarlo por dos motivos:

    1. No genera conflictos de los paquetes necesarios para
       correr Preciosa con los paquetes de sistema

    2. No instala paquetes innecesarios en el sistema

Para instalarlo ejecutar en tu shell::


    pip install virtualenv
    virtualenv --no-site-packages preciosa_ve

Una vez instalado, es necesario activar el entorno usando::

    source preciosa_ve/bin/activate

Para desactivarlo basta ejecutar ``deactivate`` en cualquier path del
terminal.


    En Windows no se puede usar el comando ``source``. Para
    activar el virtualenv luego de haber creado ``preciosa_ve``, ejecutar

        preciosa_ve\Scripts\activate


La creación del directorio ``preciosa_ve`` se hace en un directorio de
trabajo, preferentemente, para evitar modificar el directorio del
proyecto actual.

2. Instalación de los requerimientos

``Preciosa`` requiere muchos paquetes para que funcione correctamente.
Para instalar lo estrictamente necesario en tu entorno basta ejecutar::

    pip install -r requirements.txt

Opcionalmente, si querés algunos otros paquetes útiles (como IPython), podés instalar los paquetes opcionales::

    pip install -r requirements/optional.txt


.. attention::

    Para que estos comandos funcionen, tenés que ejecutarlo
    desde ``root`` de ``Preciosa`` (es decir, la carpeta que creaste cuando clonaste el repositorio) con el virtualenv activado.



Instalar y configurar Postgres y PostGIS
----------------------------------------

Como Preciosa utiliza funciones de geolocalización basadas en Geodjango, requiere una base de datos con soporte GIS. Usamos Postgres 9.1 con PostGIS >1.5 . Seguí `esta
guia <https://github.com/mgaitan/preciosa/wiki/Puesta-a-punto-de-PostgreSQL-y-PostGis-en-Ubuntu-o-Debian>`_ en la wiki de Preciosa, para instalar lo necesario.

Luego hace falta indicarle a Django la configuración de la base de datos recién creada, y te conviene hacerlo en un archivo ``local_settings.py``, que está excluído del control de versiones. Dejamos un *template* que debería funcionar sin cambios si seguiste el tutorial de instalación de la base de datos textualmente::

   cp preciosa/local_settings.py.template preciosa/local_settings.py


Crear esquemas y cargar datos
------------------------------

1. Crear base de datos

   Para crear el schema de la base de datos basta ejecutar los comandos::
  
        python manage.py syncdb --noinput

   luego::
     
        python manage.py migrate

   y luego::

        python manage.py createsuperuser


2. Cargar los fixtures::

    python manage.py loaddata fixtures/flatpages.json fixtures/blog.json fixtures/newsletter.json fixtures/ciudades.json fixtures/sucursales.json fixtures/categorias.json fixtures/marcas.json fixtures/productos.json fixtures/precios.json

Los fixtures cargan datos al schema creado en la etapa anterior.

Ejecutando ``Preciosa``
-----------------------

Primero probá si todo salió bien corriendo los tests::

    python manage.py test

Para correr ``Preciosa`` basta ejecutar::

    python manage.py runserver

Una vez ejecutado, ``Preciosa`` estará disponible en el puerto indicado en la terminal (por defecto es el 8000)

Para hacer uso del ``admin`` de ``Django`` y editar la base de datos,
basta acceder a ``/admin`` en tu browser en el puerto especificado y
acceder con el usuario y contraseña creados en ``syncdb``.


.. _virtualenv: http://www.virtualenv.org/en/latest/
