Guía de instalación
===================

El objetivo de este documento es permitir que desarrolladores puedan crear sus entornos de desarrollo rápidamente e ir a lo que interesa: contribuir con código.

En cada etapa abajo se aclara para qué sirven.

Preparación del entorno
-----------------------

1. Instalación de `virtualenv`

`virtualenv` es un componente que nos permite aislar la instalación de paquetes de la instalación del sistema. Es buena práctica utilizarlo por 2 motivos:
  1. No genera conflictos de los paquetes necesarios para correr Preciosa con los paquetes de sistema
  2. No instala paquetes innecesarios en el sistema

Para instalarlo ejecutar en tu shell:

```
pip install virtualenv
virtualenv --no-site-packages preciosa_ve
```

Una vez instalado, es necesario activar el entorno usando:

```
source preciosa_ve/bin/activate
```

Para desactivarlo basta ejecutar `deactivate` en cualquier path del terminal.

Si se trabaja en Windows, no se puede usar el comando `source`. Para activar el virtualenv luego de haber creado
`preciosa_ve`, ejectuar:

```
preciosa_ve\Scripts\activate
```

La creación del directorio preciosa_ve se hace en un directorio de trabajo, preferentemente,
para evitar modificar el directorio del proyecto actual.

2. Instalación de los requerimientos

`Preciosa` requiere muchos paquetes para que funcione correctamente. Para instalarlos en tu entorno basta ejecutar:

```
pip install -r requirements.txt
```

Atención porque para que ese comando funcione, tenés que ejecutarlo desde `root` de `Preciosa` (Es decir, la carpeta que creaste cuando clonaste el repositorio).

Instalar y configurar Postgres y PostGIS
-----------------------------------------

Seguir [esta guia](https://github.com/mgaitan/preciosa/wiki/Puesta-a-punto-de-PostgreSQL-y-PostGis-en-Ubuntu-o-Debian) en la wiki de Preciosa. 


Generación de base de datos
---------------------------

1. Crear base de datos

Para crear el schema de la base de datos basta ejecutar el comando:

```
python manage.py syncdb
```

2. Correr las migraciones

```
python manage.py cities_light
python manage.py migrate
python manage.py loaddata fixtures/blog.json fixtures/newsletter.json fixtures/ciudades.json  fixtures/sucursales.json  fixtures/categorias.json fixtures/marcas.json fixtures/productos.json fixtures/precios.json
```


3. Cargar los `fixtures` siguiendo el orden especificado en `fixtures/README.txt`

Los fixtures cargan datos al schema creado en la etapa anterior.


Ejecutando `Preciosa`
---------------------

Para correr `Preciosa` basta ejecutar:

```
python manage.py runserver
```

Una vez ejecutado, `Preciosa` estará disponible en el puerto indicado en la terminal.

Para hacer uso del `admin` de `Django` y editar la base de datos, basta acceder a `/admin` en tu browser en el puerto especificado y acceder con el usuario y contraseña creados en `syncdb`.
