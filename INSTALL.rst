Guía de instalación
===================

El objetivo de este documento es permitir que desarrolladores puedan
crear sus entornos de desarrollo rápidamente e ir a lo que interesa:
contribuir con código.

Dado que preciosa tiene una cantidad importante de dependencias y que depende de PostGIS para funcionar, vamos a utilizar Vagrant+VirtualBox como entorno de instalación del sistema. 

Esta guía está pensada principalmente para sistemas Linux Ubuntu/Debian, y está probado para VirtualBox >= 4.3 y Vagrant >= 1.3.5

.. tip::

    Una forma alternativa para desarrolladores más experimentados es `configurar tu máquina local para correr preciosa 
    <https://github.com/mgaitan/preciosa/wiki/Como-instalar-y-configurar-Preciosa-de-manera-local>`_ .


Instalación de ``Vagrant`` y ``VirtualBox``
-------------------------------------------

Para instalar y ejecutar Vagrant y VirtualBox en tu shell:

::

    sudo apt-get install vagrant virtualbox

.. attemtion::

    Si la versión de VirtualBox es menor a 4.3 podés instalar la versión para tu sistema operativo `acá <https://www.virtualbox.org/wiki/Downloads>_` 

Por último instalamos un plugin de Vagrant que es necesario para que todo funcione bien:

::

    vagrant plugin install vagrant-vbguest

   
Instalando el Entorno
---------------------

Posicionados en la carpeta raíz del repositorio instalamos el entorno de desarrollo con un solo comando:

::
    
    vagrant up

Va a tomar un tiempo la instalación porque implica bajar una máquina virtual completa pero luego de eso accedemos via ssh a una máquina virtual completa:

::

    vagrant ssh

Adentro del entorno nos posicionamos en la carpeta ``preciosa`` y creamos un superuser:

::

    cd preciosa 
    python manage.py createsuperuser 

y levantamos el server de Django:

::

    sudo python manage.py runserver 0:8000

Una vez ejecutado, ``Preciosa`` estará disponible en tu browser tecleado ``http://127.0.0.1:8000``

Para manipular la base de datos podés  acceder a ``/admin`` en tu browser en el puerto especificado e ingresar con el usuario y contraseña creados en ``createsuperuser``.


