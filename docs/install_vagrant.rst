.. _vagrant:

Creación de un entorno de desarrollo basado en Vagrant
======================================================

El objetivo de este documento es permitir que desarrolladores puedan
crear sus entornos de desarrollo rápidamente e ir a lo que interesa:
contribuir con código.

Se basa en Vagrant_, una herramienta para la creación y configuración de entornos de desarrollo virtualizados.

En una maquina virtual basada en Ubuntu, Vagrant realiza una instalación automatizada del entorno de desarrollo (configurando base de dato, dependencias, usuario, etc.) y configura la "conexión de red" y la carpeta compartida para trabajar desde la maquina física, independientemente del sistema operativo que tenga, y "ejecutar" el código en la maquina virtual.


.. tip::

    Una forma alternativa para desarrolladores mas experimentados es armar un entorno de desarrollo local


.. _Vagrant: http://vagrantup.com/


Esta guía está pensada principalmente para sistemas Linux Ubuntu/Debian, y esta probado para VirtualBox >= 4.3 y Vagrant >= 1.3.5, pero debería funcionar desde cualquier sistema operativo host. Leé la documentación_ de Vagrant para obtener información particular para tu sistema operativo.

.. _documentación: http://docs.vagrantup.com/v2/


Instalación de ``Vagrant`` y ``VirtualBox``
-------------------------------------------

Para instalar y ejecutar Vagrant y VirtualBox en tu shell:

::

    sudo apt-get install vagrant virtualbox

.. attemtion::

    Si la versión de VirtualBox es menor a 4.3 podes instalar la versión para tu sistema operativo `aca <https://www.virtualbox.org/wiki/Downloads>_`

Por ultimo instalamos un plugin de Vagrant que es necesario para que todo funcione bien:

::

    vagrant plugin install vagrant-vbguest


Instalando el Entorno
---------------------

Posicionados en la carpeta raíz del repositorio instalamos el entorno de desarrollo con un solo comando:

::

    vagrant up

Va a tomar un tiempo la instalación porque implica bajar una maquina virtual completa pero luego de eso accedemos via ssh a una maquina virtual completa:

::

    vagrant ssh

Adentro del entorno nos posicionamos en la carpeta preciosa y creamos un superuser:

::

    cd preciosa
    python manage.py createsuperuser

y levantamos el server de Django:

::

    sudo python manage.py runserver 0:8000

Una vez ejecutado, ``Preciosa`` estará disponible en tu browser tecleado http://localhost:8000

Para manipular la base de datos podes  acceder a ``/admin`` en tu browser en el puerto especificado e ingresar con el usuario y contraseña creados en ``createsuperuser``.


El script de provisión
----------------------

El script que Vagrant ejecuta para crear por primera la maquina virtual se encuentre en :path:`/tools/install.sh` y es el siguiente:

.. include:: ../tools/install.sh