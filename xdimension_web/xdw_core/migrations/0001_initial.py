# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('cms', '0001_initial.py'),
    )

    def forwards(self, orm):
        # Adding model 'Map'
        db.create_table(u'xdw_core_map', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('map_data', self.gf('json_field.fields.JSONField')(default=u'null')),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('author_name', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('author_surname', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('picture_url', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('node_count', self.gf('django.db.models.fields.IntegerField')()),
            ('node_titles', self.gf('json_field.fields.JSONField')(default=u'null')),
            ('last_node_title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('date_created', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now, db_index=True)),
            ('popularity', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('featured', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='O', max_length=1, db_index=True)),
        ))
        db.send_create_signal(u'xdw_core', ['Map'])

        # Adding model 'MapTopic'
        db.create_table(u'xdw_core_maptopic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('map', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['xdw_core.Map'])),
            ('topic', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('relevance', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'xdw_core', ['MapTopic'])

        # Adding index on 'MapTopic', fields ['topic', 'relevance']
        db.create_index(u'xdw_core_maptopic', ['topic', 'relevance'])


    def backwards(self, orm):
        # Removing index on 'MapTopic', fields ['topic', 'relevance']
        db.delete_index(u'xdw_core_maptopic', ['topic', 'relevance'])

        # Deleting model 'Map'
        db.delete_table(u'xdw_core_map')

        # Deleting model 'MapTopic'
        db.delete_table(u'xdw_core_maptopic')


    models = {
        u'xdw_core.map': {
            'Meta': {'object_name': 'Map'},
            'author_name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'author_surname': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'featured': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_node_title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'map_data': ('json_field.fields.JSONField', [], {'default': "u'null'"}),
            'node_count': ('django.db.models.fields.IntegerField', [], {}),
            'node_titles': ('json_field.fields.JSONField', [], {'default': "u'null'"}),
            'picture_url': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'popularity': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'})
        },
        u'xdw_core.maptopic': {
            'Meta': {'object_name': 'MapTopic', 'index_together': "[['topic', 'relevance']]"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['xdw_core.Map']"}),
            'relevance': ('django.db.models.fields.IntegerField', [], {}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['xdw_core']
