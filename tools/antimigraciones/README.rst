Antimigraciones
---------------

En este paquete van aquellos scripts para migracion o importación de datos que por su uso único, su falta de calidad o sus maneras non-sanctas de cumplir su objetivo, no ameritan/califican para un datamigration o un management command

*Antimigraciones* refiere al abuso de antipatrones que te
podés encontrar por acá.

.. attention::

    hacé backup antes de ejecutar cualquier cosa


Cómo ejecutar
+++++++++++++

Como la mayoria son scripts que trabajan con los modelos de
Preciosa, necesitas tener django correctamente configurado: ese es el motivo por el que no funcionará correr los scripts *directamente* con el interprete de Python.

La forma recomendada es utilizar el shell de django, a traves de IPython (dependencia listada  en ``requirements/optional.txt``)::

    $ python manage.py shell_plus

y luego utilizar el *"magic"* ``%run`` ::

    In [1]: %run  tools/antimigraciones/<ANTIPATRON>.py


