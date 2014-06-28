# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Region'
        db.create_table(u'acuerdos_region', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'acuerdos', ['Region'])

        # Adding M2M table for field provincias on 'Region'
        m2m_table_name = db.shorten_name(u'acuerdos_region_provincias')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_region', models.ForeignKey(orm[u'acuerdos.region'], null=False)),
            ('to_region', models.ForeignKey(orm[u'cities_light.region'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_region_id', 'to_region_id'])

        # Adding M2M table for field ciudades_incluidas on 'Region'
        m2m_table_name = db.shorten_name(u'acuerdos_region_ciudades_incluidas')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('region', models.ForeignKey(orm[u'acuerdos.region'], null=False)),
            ('city', models.ForeignKey(orm[u'cities_light.city'], null=False))
        ))
        db.create_unique(m2m_table_name, ['region_id', 'city_id'])

        # Adding M2M table for field ciudades_excluidas on 'Region'
        m2m_table_name = db.shorten_name(u'acuerdos_region_ciudades_excluidas')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('region', models.ForeignKey(orm[u'acuerdos.region'], null=False)),
            ('city', models.ForeignKey(orm[u'cities_light.city'], null=False))
        ))
        db.create_unique(m2m_table_name, ['region_id', 'city_id'])

        # Adding M2M table for field ciudades on 'Region'
        m2m_table_name = db.shorten_name(u'acuerdos_region_ciudades')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('region', models.ForeignKey(orm[u'acuerdos.region'], null=False)),
            ('city', models.ForeignKey(orm[u'cities_light.city'], null=False))
        ))
        db.create_unique(m2m_table_name, ['region_id', 'city_id'])

        # Adding model 'Acuerdo'
        db.create_table(u'acuerdos_acuerdo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['acuerdos.Region'])),
        ))
        db.send_create_signal(u'acuerdos', ['Acuerdo'])

        # Adding M2M table for field sucursales on 'Acuerdo'
        m2m_table_name = db.shorten_name(u'acuerdos_acuerdo_sucursales')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('acuerdo', models.ForeignKey(orm[u'acuerdos.acuerdo'], null=False)),
            ('sucursal', models.ForeignKey(orm[u'precios.sucursal'], null=False))
        ))
        db.create_unique(m2m_table_name, ['acuerdo_id', 'sucursal_id'])

        # Adding M2M table for field cadenas on 'Acuerdo'
        m2m_table_name = db.shorten_name(u'acuerdos_acuerdo_cadenas')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('acuerdo', models.ForeignKey(orm[u'acuerdos.acuerdo'], null=False)),
            ('cadena', models.ForeignKey(orm[u'precios.cadena'], null=False))
        ))
        db.create_unique(m2m_table_name, ['acuerdo_id', 'cadena_id'])

        # Adding model 'PrecioEnAcuerdo'
        db.create_table(u'acuerdos_precioenacuerdo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('acuerdo', self.gf('django.db.models.fields.related.ForeignKey')(related_name='precios_en_acuerdo', to=orm['acuerdos.Acuerdo'])),
            ('producto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['precios.Producto'])),
            ('precio', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
        ))
        db.send_create_signal(u'acuerdos', ['PrecioEnAcuerdo'])


    def backwards(self, orm):
        # Deleting model 'Region'
        db.delete_table(u'acuerdos_region')

        # Removing M2M table for field provincias on 'Region'
        db.delete_table(db.shorten_name(u'acuerdos_region_provincias'))

        # Removing M2M table for field ciudades_incluidas on 'Region'
        db.delete_table(db.shorten_name(u'acuerdos_region_ciudades_incluidas'))

        # Removing M2M table for field ciudades_excluidas on 'Region'
        db.delete_table(db.shorten_name(u'acuerdos_region_ciudades_excluidas'))

        # Removing M2M table for field ciudades on 'Region'
        db.delete_table(db.shorten_name(u'acuerdos_region_ciudades'))

        # Deleting model 'Acuerdo'
        db.delete_table(u'acuerdos_acuerdo')

        # Removing M2M table for field sucursales on 'Acuerdo'
        db.delete_table(db.shorten_name(u'acuerdos_acuerdo_sucursales'))

        # Removing M2M table for field cadenas on 'Acuerdo'
        db.delete_table(db.shorten_name(u'acuerdos_acuerdo_cadenas'))

        # Deleting model 'PrecioEnAcuerdo'
        db.delete_table(u'acuerdos_precioenacuerdo')


    models = {
        u'acuerdos.acuerdo': {
            'Meta': {'object_name': 'Acuerdo'},
            'cadenas': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['precios.Cadena']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['acuerdos.Region']"}),
            'sucursales': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['precios.Sucursal']", 'symmetrical': 'False'})
        },
        u'acuerdos.precioenacuerdo': {
            'Meta': {'object_name': 'PrecioEnAcuerdo'},
            'acuerdo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'precios_en_acuerdo'", 'to': u"orm['acuerdos.Acuerdo']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'precio': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'producto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['precios.Producto']"})
        },
        u'acuerdos.region': {
            'Meta': {'object_name': 'Region'},
            'ciudades': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'region_en_acuerdo'", 'symmetrical': 'False', 'to': u"orm['cities_light.City']"}),
            'ciudades_excluidas': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'excluida_de_region_acuerdo'", 'symmetrical': 'False', 'to': u"orm['cities_light.City']"}),
            'ciudades_incluidas': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'incluida_en_region_acuerdo'", 'symmetrical': 'False', 'to': u"orm['cities_light.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'provincias': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'incluida_en_region_acuerdo'", 'symmetrical': 'False', 'to': u"orm['cities_light.Region']"})
        },
        u'cities_light.city': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('region', 'name'),)", 'object_name': 'City'},
            'alternate_names': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities_light.Country']"}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'feature_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'geoname_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '5', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '5', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_ascii': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'population': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities_light.Region']", 'null': 'True', 'blank': 'True'}),
            'search_names': ('cities_light.models.ToSearchTextField', [], {'default': "''", 'max_length': '4000', 'db_index': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name_ascii'"})
        },
        u'cities_light.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country'},
            'alternate_names': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'code2': ('django.db.models.fields.CharField', [], {'max_length': '2', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'code3': ('django.db.models.fields.CharField', [], {'max_length': '3', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'continent': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'}),
            'geoname_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'name_ascii': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name_ascii'"}),
            'tld': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '5', 'blank': 'True'})
        },
        u'cities_light.region': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('country', 'name'),)", 'object_name': 'Region'},
            'alternate_names': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities_light.Country']"}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'geoname_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'geoname_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_ascii': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name_ascii'"})
        },
        u'precios.cadena': {
            'Meta': {'object_name': 'Cadena'},
            'cadena_madre': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['precios.Cadena']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': (u'django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'logo_changed': ('model_utils.fields.MonitorField', [], {'default': 'datetime.datetime.now', u'monitor': "'logo'"}),
            'logo_cropped': (u'django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'precios.categoria': {
            'Meta': {'object_name': 'Categoria'},
            'busqueda': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'oculta': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'precios.empresafabricante': {
            'Meta': {'object_name': 'EmpresaFabricante'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': (u'django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'logo_changed': ('model_utils.fields.MonitorField', [], {'default': 'datetime.datetime.now', u'monitor': "'logo'"}),
            'logo_cropped': (u'django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'precios.marca': {
            'Meta': {'unique_together': "(('nombre', 'fabricante'),)", 'object_name': 'Marca'},
            'fabricante': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['precios.EmpresaFabricante']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': (u'django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'logo_changed': ('model_utils.fields.MonitorField', [], {'default': 'datetime.datetime.now', u'monitor': "'logo'"}),
            'logo_cropped': (u'django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'precios.producto': {
            'Meta': {'object_name': 'Producto'},
            'busqueda': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'categoria': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'productos'", 'to': u"orm['precios.Categoria']"}),
            'contenido': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '1', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'foto': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marca': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['precios.Marca']", 'null': 'True', 'blank': 'True'}),
            'notas': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'oculto': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unidad_medida': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'unidades_por_lote': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'upc': ('django.db.models.fields.CharField', [], {'max_length': '13', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'precios.sucursal': {
            'Meta': {'unique_together': "(('direccion', 'ciudad'),)", 'object_name': 'Sucursal'},
            'busqueda': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'cadena': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sucursales'", 'null': 'True', 'to': u"orm['precios.Cadena']"}),
            'ciudad': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cities_light.City']"}),
            'cp': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'direccion': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'horarios': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'telefono': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'ubicacion': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['acuerdos']