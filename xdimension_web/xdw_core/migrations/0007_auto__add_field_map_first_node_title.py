# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Map.first_node_title'
        db.add_column(u'xdw_core_map', 'first_node_title',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=500),
                      keep_default=False)
        for mp in orm.Map.objects.all():
            if not mp.map_data:
                continue
            try:
                mp.first_node_title = mp.map_data['map']['startNode']['title']
            except KeyError:
                print 'first node not found on map {}'.format(mp.pk)
            try:
                mp.last_node_title = mp.map_data['map']['endNode']['title']
            except KeyError:
                print 'last node not found on map {}'.format(mp.pk)
            mp.save()

    def backwards(self, orm):
        # Deleting field 'Map.first_node_title'
        db.delete_column(u'xdw_core_map', 'first_node_title')


    models = {
        u'xdw_core.map': {
            'Meta': {'object_name': 'Map'},
            'author_name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'author_surname': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'featured': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'first_node_title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_node_title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'map_data': ('json_field.fields.JSONField', [], {'default': "u'null'"}),
            'net': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'node_count': ('django.db.models.fields.IntegerField', [], {}),
            'node_titles': ('json_field.fields.JSONField', [], {'default': "u'null'"}),
            'picture_url': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'popularity': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1', 'db_index': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'thumbnail_status': ('django.db.models.fields.CharField', [], {'default': "'x'", 'max_length': '1', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'})
        },
        u'xdw_core.maptopic': {
            'Meta': {'object_name': 'MapTopic', 'index_together': "[['topic', 'relevance']]"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['xdw_core.Map']"}),
            'relevance': ('django.db.models.fields.FloatField', [], {}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'xdw_core.topic': {
            'Meta': {'object_name': 'Topic'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'topic': ('django.db.models.fields.CharField', [], {'max_length': '500', 'primary_key': 'True'})
        }
    }

    complete_apps = ['xdw_core']
