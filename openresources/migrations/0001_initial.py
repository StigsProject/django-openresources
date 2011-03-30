# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Resource'
        db.create_table('openresources_resource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('shortname', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=200, db_index=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openresources.ResourceTemplate'], null=True, blank=True)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('protected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('openresources', ['Resource'])

        # Adding model 'Tag'
        db.create_table('openresources_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('value', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('resource', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tags', to=orm['openresources.Resource'])),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('value_date', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('value_relation', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='relations_to', null=True, to=orm['openresources.Resource'])),
        ))
        db.send_create_signal('openresources', ['Tag'])

        # Adding model 'View'
        db.create_table('openresources_view', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('shortname', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100, db_index=True)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('protected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order_by', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('include_past', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('include_current', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('include_upcoming', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_map', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('openresources', ['View'])

        # Adding M2M table for field sub_views on 'View'
        db.create_table('openresources_view_sub_views', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_view', models.ForeignKey(orm['openresources.view'], null=False)),
            ('to_view', models.ForeignKey(orm['openresources.view'], null=False))
        ))
        db.create_unique('openresources_view_sub_views', ['from_view_id', 'to_view_id'])

        # Adding model 'TagQuery'
        db.create_table('openresources_tagquery', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('boolean', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('exclude', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('comparison', self.gf('django.db.models.fields.IntegerField')()),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('view', self.gf('django.db.models.fields.related.ForeignKey')(related_name='queries', to=orm['openresources.View'])),
        ))
        db.send_create_signal('openresources', ['TagQuery'])

        # Adding model 'Icon'
        db.create_table('openresources_icon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal('openresources', ['Icon'])

        # Adding model 'TagMapping'
        db.create_table('openresources_tagmapping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('show_in_list', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('icon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openresources.Icon'], null=True, blank=True)),
            ('subicon', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('view', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mappings', to=orm['openresources.View'])),
        ))
        db.send_create_signal('openresources', ['TagMapping'])

        # Adding model 'Area'
        db.create_table('openresources_area', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('bounds', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('openresources', ['Area'])

        # Adding model 'Context'
        db.create_table('openresources_context', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openresources.Area'], null=True, blank=True)),
        ))
        db.send_create_signal('openresources', ['Context'])

        # Adding model 'ResourceTemplate'
        db.create_table('openresources_resourcetemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('shortname', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=100, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('openresources', ['ResourceTemplate'])

        # Adding model 'TagTemplateGroup'
        db.create_table('openresources_tagtemplategroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='groups', to=orm['openresources.ResourceTemplate'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('openresources', ['TagTemplateGroup'])

        # Adding model 'TagTemplate'
        db.create_table('openresources_tagtemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('multiple', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tags', to=orm['openresources.ResourceTemplate'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tags', to=orm['openresources.TagTemplateGroup'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('openresources', ['TagTemplate'])

        # Adding model 'UserProfile'
        db.create_table('openresources_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='resources_profile', unique=True, to=orm['auth.User'])),
            ('context', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openresources.Context'], null=True, blank=True)),
        ))
        db.send_create_signal('openresources', ['UserProfile'])


    def backwards(self, orm):
        
        # Deleting model 'Resource'
        db.delete_table('openresources_resource')

        # Deleting model 'Tag'
        db.delete_table('openresources_tag')

        # Deleting model 'View'
        db.delete_table('openresources_view')

        # Removing M2M table for field sub_views on 'View'
        db.delete_table('openresources_view_sub_views')

        # Deleting model 'TagQuery'
        db.delete_table('openresources_tagquery')

        # Deleting model 'Icon'
        db.delete_table('openresources_icon')

        # Deleting model 'TagMapping'
        db.delete_table('openresources_tagmapping')

        # Deleting model 'Area'
        db.delete_table('openresources_area')

        # Deleting model 'Context'
        db.delete_table('openresources_context')

        # Deleting model 'ResourceTemplate'
        db.delete_table('openresources_resourcetemplate')

        # Deleting model 'TagTemplateGroup'
        db.delete_table('openresources_tagtemplategroup')

        # Deleting model 'TagTemplate'
        db.delete_table('openresources_tagtemplate')

        # Deleting model 'UserProfile'
        db.delete_table('openresources_userprofile')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'openresources.area': {
            'Meta': {'object_name': 'Area'},
            'bounds': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'openresources.context': {
            'Meta': {'object_name': 'Context'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['openresources.Area']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'openresources.icon': {
            'Meta': {'ordering': "['name']", 'object_name': 'Icon'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'openresources.resource': {
            'Meta': {'ordering': "['name']", 'object_name': 'Resource'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'protected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shortname': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['openresources.ResourceTemplate']", 'null': 'True', 'blank': 'True'})
        },
        'openresources.resourcetemplate': {
            'Meta': {'object_name': 'ResourceTemplate'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'shortname': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        'openresources.tag': {
            'Meta': {'ordering': "['creation_date']", 'object_name': 'Tag'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tags'", 'to': "orm['openresources.Resource']"}),
            'value': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'value_date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'value_relation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'relations_to'", 'null': 'True', 'to': "orm['openresources.Resource']"})
        },
        'openresources.tagmapping': {
            'Meta': {'ordering': "['order', 'creation_date']", 'object_name': 'TagMapping'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'icon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['openresources.Icon']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_in_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subicon': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'view': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mappings'", 'to': "orm['openresources.View']"})
        },
        'openresources.tagquery': {
            'Meta': {'ordering': "['order', 'creation_date']", 'object_name': 'TagQuery'},
            'boolean': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'comparison': ('django.db.models.fields.IntegerField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'exclude': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'view': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'queries'", 'to': "orm['openresources.View']"})
        },
        'openresources.tagtemplate': {
            'Meta': {'ordering': "['group', 'order']", 'object_name': 'TagTemplate'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tags'", 'to': "orm['openresources.TagTemplateGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'multiple': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tags'", 'to': "orm['openresources.ResourceTemplate']"}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'openresources.tagtemplategroup': {
            'Meta': {'ordering': "['template', 'order']", 'object_name': 'TagTemplateGroup'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'to': "orm['openresources.ResourceTemplate']"})
        },
        'openresources.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'context': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['openresources.Context']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'resources_profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'openresources.view': {
            'Meta': {'ordering': "['shortname']", 'object_name': 'View'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'include_past': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'include_upcoming': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order_by': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'protected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shortname': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'show_map': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sub_views': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'sub_views_rel_+'", 'null': 'True', 'to': "orm['openresources.View']"})
        }
    }

    complete_apps = ['openresources']
