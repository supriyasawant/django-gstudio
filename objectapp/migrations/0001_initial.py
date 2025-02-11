import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Objecttype'
        db.create_table('objectapp_Objecttype', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('objectapp', ['Objecttype'])

        # Adding model 'Gbobject'
        db.create_table('objectapp_gbobject', (
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('comment_enabled', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('excerpt', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('end_publication', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2042, 3, 15, 0, 0))),
            ('start_publication', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('objectapp', ['Gbobject'])

        # Adding M2M table for field sites on 'Gbobject'
        db.create_table('objectapp_gbobject_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gbobject', models.ForeignKey(orm['objectapp.gbobject'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('objectapp_gbobject_sites', ['gbobject_id', 'site_id'])

        # Adding M2M table for field related on 'Gbobject'
        db.create_table('objectapp_gbobject_related', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_gbobject', models.ForeignKey(orm['objectapp.gbobject'], null=False)),
            ('to_gbobject', models.ForeignKey(orm['objectapp.gbobject'], null=False))
        ))
        db.create_unique('objectapp_gbobject_related', ['from_gbobject_id', 'to_gbobject_id'])

        # Adding M2M table for field objecttypes on 'Gbobject'
        db.create_table('objectapp_gbobject_objecttypes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gbobject', models.ForeignKey(orm['objectapp.gbobject'], null=False)),
            ('Objecttype', models.ForeignKey(orm['objectapp.Objecttype'], null=False))
        ))
        db.create_unique('objectapp_gbobject_objecttypes', ['gbobject_id', 'Objecttype_id'])

        # Adding M2M table for field authors on 'Gbobject'
        db.create_table('objectapp_gbobject_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gbobject', models.ForeignKey(orm['objectapp.gbobject'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('objectapp_gbobject_authors', ['gbobject_id', 'user_id'])

    def backwards(self, orm):

        # Deleting model 'Objecttype'
        db.delete_table('objectapp_Objecttype')

        # Deleting model 'Gbobject'
        db.delete_table('objectapp_gbobject')

        # Removing M2M table for field sites on 'Gbobject'
        db.delete_table('objectapp_gbobject_sites')

        # Removing M2M table for field related on 'Gbobject'
        db.delete_table('objectapp_gbobject_related')

        # Removing M2M table for field objecttypes on 'Gbobject'
        db.delete_table('objectapp_gbobject_objecttypes')

        # Removing M2M table for field authors on 'Gbobject'
        db.delete_table('objectapp_gbobject_authors')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sites.site': {
            'Meta': {'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'objectapp.Objecttype': {
            'Meta': {'object_name': 'Objecttype'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'objectapp.gbobject': {
            'Meta': {'object_name': 'Gbobject'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'blank': 'True'}),
            'objecttypes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['objectapp.Objecttype']"}),
            'comment_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'end_publication': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2042, 3, 15, 0, 0)'}),
            'excerpt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'related': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_rel_+'", 'null': 'True', 'to': "orm['objectapp.Gbobject']"}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'start_publication': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['objectapp']
